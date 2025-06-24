import secrets
import base64
import hashlib
import string
from urllib.parse import urlencode
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import JsonResponse
from django.views import View
from django.shortcuts import redirect
from django.shortcuts import render
from django_q.tasks import async_task


from YP.logger import logger
from .models import Integrations, Products, Categories
from .vk_sync import ProductIntegrations
from .get_from_sbis import catalog_sync


def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge


def generate_random_string(length=32):
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def login_page(request):
    return render(request, 'vk_api/vk_login.html')


def start_vk_login(request):
    code_verifier, code_challenge = generate_pkce_pair()
    state = generate_random_string(32)

    Integrations.objects.create(
        state=state,
        code_verifier=code_verifier,
        code_challenge=code_challenge,
    )
    logger.info(f"Создал объект модели Integrations."
                f"\nstate - {state}\ncode_verifier - {code_verifier}\ncode_challenge - {code_challenge}")

    url = (f"https://id.vk.com/authorize?"
           f"response_type=code&"
           f"client_id=53476139&"
           f"scope=market&"
           f"redirect_uri=https%3A%2F%2Fparsx.ru%2Fvk_login%2Faccept_requests%2F&"
           f"state={state}&"
           f"code_challenge={code_challenge}&"
           f"code_challenge_method=S256")
    return redirect(url)


class VkAcceptCodeView(View):
    @staticmethod
    def get_access_token(code_verifier, code, device_id, state):
        url = "https://id.vk.com/oauth2/auth"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "redirect_uri": "https://parsx.ru/vk_login/accept_requests/",
            "code": code,
            "client_id": "53476139",
            "device_id": device_id,
            "state": state
        }

        response = requests.post(url, headers=headers, data=data).json()
        logger.debug('Post-запрос для авторизации без SDK')
        logger.debug(f'url - {url}')
        logger.debug(f'headers - {headers}')
        logger.debug(f'data - {data}')
        if response.get("error_description"):
            logger.error(f"""Ошибка при попытке получить access_token. \n{response.get("error_description")}""")
        else:
            logger.debug('Ответ')
            logger.debug(response)
            return response.get("refresh_token"), response.get("access_token")

    def get(self, request):
        request_data = request.GET
        code = request_data.get("code")
        state = request_data.get("state")
        device_id = request_data.get("device_id")

        "берем code_verifier для последнего появившегося объекта из БД"
        last_object = Integrations.objects.get(state=state)
        if last_object:
            code_verifier = last_object.code_verifier
        else:
            logger.critical("The table is empty")
            return None

        "запрашиваем пару refresh_token и access_token"
        refresh_token, access_token = self.get_access_token(
            code_verifier=code_verifier,
            code=code,
            device_id=device_id,
            state=state
        )
        "Add new data to DB"
        obj, created = Integrations.objects.update_or_create(
            state=state,
            defaults={
                'device_id': device_id,
                'authorization_code': code,
                'refresh_token': refresh_token,
                'access_token': access_token,
            }
        )

        # Обработка отсутствующих параметров
        if not code:
            return JsonResponse({"error": "Missing 'code' parameter"}, status=400)

        return JsonResponse({
            "message": "Integration saved successfully",
            # "integration_id": integration.id
        })


class CheckAuthorizationCodeAPIView(APIView):
    def post(self, request):
        # code = request.data.get('authorization_code')
        logger.warning('Используется ненадежный способ получения кода (по последнему созданному объекту)')
        last_obj = Integrations.objects.latest('id')
        code = last_obj.authorization_code

        product_data = request.data.get('product_data')

        if not code or not product_data:
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prod_vk_id = self.run_custom_logic(code, product_data)
        except Exception as e:
            logger.error(f"Ошибка синхронизации - {e}")
        else:
            return Response({"status": "OK", "prod_vk_id": prod_vk_id})

    @staticmethod
    def run_custom_logic(code, product_data):
        integrations = ProductIntegrations()
        prod_vk_id = integrations.sync_one_prod(code, product_data)
        logger.info(f"prod_vk_id - {prod_vk_id}")
        return prod_vk_id


class VkUpdaterAPIView(APIView):
    def post(self, request):
        """В этом месте необходимо реализовать логику, которая возьмет
                customer_id и authorization_code и проверит, есть ли такая пара в БД"""
        # check_customer_id(customer_id, authorization_code)

        # Синхронизируем СБИС и ВК-маркет
        customer_id = request.data.get('customer_id')
        if not customer_id:
            logger.error(f"Не переданы данные по customer_id")
            return Response({"status": "ERROR", "error_desc": f"Не переданы данные по customer_id"})

        method = request.data.get('method')
        if not method:
            logger.error(f"Не передан method")
            return Response({"status": "ERROR",
                             "error_desc": f"Не передан method"})
        elif method not in ("db_update", "vk_update"):
            logger.error(f"method может иметь только 2 типа значения - db_update, vk_update")
            return Response({"status": "ERROR",
                             "error_desc": f"method может иметь только 2 типа значения - db_update, vk_update"})

        if method == "db_update":
            logger.info(f"Запускаю фоновую задачу по синхронизации БД со СБИС")
            # catalog_sync(customer_id)
            async_task('vk_sync.tasks.catalog_sync_wrapper', customer_id)
            return Response({"status": "OK",
                             "message": f"Ожидайте 10 минут до окончания синхронизации каталога"})

        logger.debug(f"customer_id - {customer_id}")

        try:
            products = self.get_vk_products()
        except Exception as e:
            logger.error(f"Ошибка получения товаров из ВК - {e}")
            return Response({"status": "ERROR", "error_desc": f"Ошибка получения товаров из ВК - {e}"})

        try:
            self.vk_updater(customer_id)
        except Exception as e:
            logger.error(f"Ошибка обновления товаров ВК - {e}")
            return Response({"status": "ERROR", "error_desc": f"Ошибка получения товаров из ВК - {e}"})
        return Response({"status": "OK", "prod_vk_id": products})

    @staticmethod
    def get_vk_products():
        ""
        logger.warning('Используется ненадежный способ получения кода (по последнему созданному объекту)')
        last_obj = Integrations.objects.latest('id')
        code = last_obj.authorization_code

        PI = ProductIntegrations()
        products = PI.get_products(auth_code=code)

        return products

    @staticmethod
    def vk_updater(customer_id):
        logger.debug('Получаем список товаров, принадлежащих пользователю')
        db_products = Products.objects.filter(customer=customer_id)

        sync = ProductIntegrations()
        last_obj = Integrations.objects.latest('id')
        code = last_obj.authorization_code

        logger.debug("получаем access_token")
        access_token = sync.auth(code)
        logger.debug(f'access_token - {access_token}')
        if not access_token:
            logger.error("Не удалось получить access_token")
            return None

        logger.debug(f'Пытаюсь вывести db_products...')
        logger.debug(db_products)
        for product in db_products:
            logger.debug("Формируем product_info")
            """('vk_id', 'sbis_id', 'site_link', 'pic_urls', 'name', 'description', 'price', 'old_price', 'url')"""
            product_info = {
                'sbis_id': product.sbis_id,
                'name': product.name,
                'description': product.description,
                'pic_urls': product.images,
                'price': product.price,
                'old_price': product.old_price,
                'site_link': product.unisiter_url,
            }
            logger.debug(f"product_info - {product_info}")
            if product.vk_id: #Если товар есть в ВК маркет, обновляем его значения
                logger.debug(f"{product.name} уже есть в ВК-маркет, обновляю его")
                product_info['vk_id'] = product.vk_id
                result = sync.update_product(access_token, product_info)
                logger.debug(f"Результат обновления - {result}")
                if result == {"response": 1}:
                    logger.debug(f'Обновление {product.name} прошло успешно!')
            else: #Если такого товара нет, добавляем его
                logger.debug(f"{product.name} нет в ВК-маркет, добавляю его")
                category = product.objects.select_related('category_id').get(sbis_id=product.sbis_id)
                vk_category_id = category.category_id.vk_id
                product_info["vk_category_id"] = vk_category_id

                prod_vk_id = sync.add_prod(access_token, product_info)
                logger.debug('добавляем в товар значение для поля vk_id')
                product.update(vk_id=prod_vk_id)

