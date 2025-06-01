import secrets
import base64
import hashlib
import string
from urllib.parse import urlencode
import requests

from rest_framework import generics
from django.http import JsonResponse
from .models import Integrations
from django.views import View
from django.shortcuts import redirect
from django.shortcuts import render


from YP.logger import logger
from .models import Integrations, Products, Categories
from .serializers import IntegrationsSerializer


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
        if response.get("error_description"):
            logger.error(f"""Ошибка при попытке получить access_token. \n{response.get("error_description")}""")
        else:
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
        logger.info(f'obj: {obj}\n created: {created}')

        # Обработка отсутствующих параметров
        if not code:
            return JsonResponse({"error": "Missing 'code' parameter"}, status=400)

        return JsonResponse({
            "message": "Integration saved successfully",
            # "integration_id": integration.id
        })


class IntegrationsListCreateAPIView(generics.ListCreateAPIView):
    queryset = Integrations.objects.all()
    serializer_class = IntegrationsSerializer
