import requests
import json
from pathlib import Path
import time

from .models import Integrations, Products, Categories
from YP.logger import logger


SBIS_TOKEN = "rbbew4LZMbof6GNJEWy0ZAz8jRhS3qQRaMLuiWQbcNHUyfj2WCpOswpo86FJyKoEKIT2Rqmmzufc3YHMdp8ZggucdnWRQTvQ56fMP4RW1pHsbwVUxwyZv3"
SBIS_PRICE_ID = 205
VK_owner_id = 229250771


def pic_download(sbis_id, pic_urls):
    '''Итерируясь по списку товаров, ищем обновления в поле БД "images_response", если обновление есть,
    скачиваем картинки и вставляем обновление в БД'''
    parent_dir = Path(__file__).resolve().parent
    media_dir = parent_dir / "media" / "products"

    if pic_urls:
        cnt_img = 1
        for img in pic_urls:
            url = 'https://api.sbis.ru/retail/' + img
            file_name = sbis_id + '-' + str(cnt_img)
            file_path = media_dir / f"{file_name}.jpg"

            response = requests.get(url, headers={"X-SBISAccessToken": SBIS_TOKEN})
            with open(file_path, 'wb') as file:
                file.write(response.content)
                cnt_img += 1


class ProductIntegrations:
    def __init__(self, sbis_data=None):
        self.sbis_data = sbis_data
        parent_dir = Path(__file__).resolve().parent
        self.media_dir = parent_dir / "media" / "products"

    @staticmethod
    def get_access(refresh_token, device_id, state):
        "Для получения access_token"
        url = "https://id.vk.com/oauth2/auth"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": "53476139",
            "device_id": device_id,
            "state": state,
            "scope": "market"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers).json()
        try:
            refresh_token = response.get('refresh_token')
            access_token = response.get('access_token')

            if refresh_token:
                return refresh_token, access_token
        except Exception as e:
            logger.error(f'Ошибка при попытке получить ответ {e}')

    def auth(self, auth_code):
        tokens = Integrations.objects.get(authorization_code=auth_code)

        refresh_token, device_id, state = tokens.refresh_token, tokens.device_id, tokens.state

        token_data = self.get_access(refresh_token, device_id, state)
        if token_data:
            try:
                new_refresh_token, access_token = token_data
            except Exception as E:
                logger.error(f"Не удалось извлечь данные, ошибка {E}")
            else:
                try:
                    tokens.refresh_token = new_refresh_token
                    tokens.access_token = access_token
                    tokens.save()
                    return access_token
                except Exception as E:
                    logger.error(f"Ошибка при обновлении токенов через djangoORM {E}")
        else:
            logger.error('Не удалось получить Токены')

    @staticmethod
    def get_url(access_token, one_photo=True):
        "Метод для получения URL для загрузки изображения"
        data = {
            'group_id': VK_owner_id,
            'access_token': access_token,
            'v': '5.199',
        }
        "Если планируется загрузить более одного фото, добавляем параметр bulk"
        if one_photo:
            data['bulk'] = 1
        resp = requests.post('https://api.vk.com/method/market.getProductPhotoUploadServer', data=data).json()

        if resp.get('error'):
            logger.error(f'''Ошибка в ответ на запрос - {resp.get('error')}''')
            return None

        upload_url, bulk_upload = resp['response'].get('upload_url'), resp['response'].get('bulk_upload')

        if upload_url:
            return upload_url.split('token=')[1]
        else:
            return bulk_upload

    @staticmethod
    def download_photo(upload_url, photo_path):
        "Аргумент photo или list или str"
        params = {
            'token': upload_url,
        }

        if type(photo_path) is str:
            files = {'file': open(photo_path, 'rb')}
        else:
            files = {}
            cnt = 1
            for photo in photo_path:
                files[f'file{cnt}'] = open(photo, 'rb')

        response = requests.post('https://pu.vk.com/gu-s/photo/v2/upload', params=params, files=files).json()
        if response.get('error_msg'):
            logger.error(f'''Ошибка в ответ на запрос - {response.get('error_msg')}''')
            return None
        return response

    @staticmethod
    def get_photo_id(photo_data, access_token, one_photo=True):
        method = 'market.saveProductPhoto' if one_photo else 'market.saveProductPhotoBulk'
        upload_response = json.dumps(photo_data)

        data = {
            'upload_response': upload_response,
            'access_token': access_token,
            'v': '5.199',
        }

        response = requests.post(f'''https://api.vk.com/method/{method}''', data=data).json()
        if response.get('error'):
            logger.error(f'''Ошибка в ответ на запрос - {response['error']['error_msg']}''')
            return None
        return response['response'].get('photo_id')

    @staticmethod
    def add_product(category_id, main_photo_id, name, desc, site_link, price, old_price, access_token):
        price = str(price)
        """Передалать метод таким образом, чтобы параметры запроса добавлялись в словарь в зависимости от наличия.
        Например, если old_price не будет передан, возникнет ошибка."""
        data = {
            'owner_id': -VK_owner_id,
            'name': name,
            'description': desc,
            'category_id': category_id,
            'main_photo_id': main_photo_id,
            'access_token': access_token,
            'v': '5.199',
            'price': price,
            'old_price': old_price
        }

        if site_link:
            data['url'] = site_link

        response = requests.post('https://api.vk.com/method/market.add', data=data).json()
        logger.info(response)
        time.sleep(1)
        if response.get('response'):
            return response['response']['market_item_id']

    @staticmethod
    def product_delete(prod_id, access_token):
        data = {
            'owner_id': -VK_owner_id,
            'access_token': access_token,
            'item_id': prod_id,
            'v': '5.199',
        }

        response = requests.post('https://api.vk.com/method/market.delete', data=data).json()
        if response.get('error'):
            logger.error(f'''Ошибка в ответ на запрос - {response['error']['error_msg']}''')

    def get_products(self, auth_code):
        # получаем access_token
        access_token = self.auth(auth_code)
        if not access_token:
            logger.error("Не удалось получить access_token")
            return None

        data = {
            'owner_id': -VK_owner_id,
            'access_token': access_token,
            'v': '5.199',
        }

        response = requests.post('https://api.vk.com/method/market.get', data=data).json()

        if response.get('error_msg'):
            logger.error(f'''Ошибка в ответ на запрос - {response.get('error_msg')}''')
            return None

        logger.debug(f'''Получено {response['response']['count']}''')

        return response['response']['items']

    def add_prod(self, access_token, product_info):
        """
        Метод для добавления нового товара
        :param access_token:
        :param product_info:
        :return:
        """
        sbis_id = product_info['sbis_id']
        pic_urls = product_info['pic_urls']
        vk_category_id = product_info['vk_category_id']
        name = product_info['name']
        desc = product_info['description']
        site_link = product_info['url']
        price = product_info['price']
        old_price = product_info['old_price']

        "Скачиваем фото"
        logger.debug(f"Запускаю логику добавления товара")
        pic_download(sbis_id, pic_urls)
        main_photo_path = self.media_dir / f"{sbis_id}-1.jpg"
        if not main_photo_path.is_file():
            logger.warning(f'изображения нет в каталоге ({main_photo_path}), пропускаем итерацию с товаром {name}')
            return 'изображения нет в каталоге'

        url = self.get_url(access_token)
        product_data = self.download_photo(url, photo_path=str(main_photo_path))
        photo_id = self.get_photo_id(product_data, access_token=access_token)
        prod_vk_id = self.add_product(vk_category_id, photo_id, name=name, desc=desc, site_link=site_link,
                                      price=price, old_price=old_price, access_token=access_token)

        # product = Products.objects.update(sbis_id=sbis_id, )
        return prod_vk_id

    def update_product(self, access_token: str, product_info: dict):
        """
        Обновляет данные товара.
        :param access_token: используется для получения access_token
        :param product_info: ('vk_id', 'sbis_id', 'site_link', 'pic_urls', 'name', 'description', 'price', 'old_price', 'url')
        Формирует параметры запроса. Имеет обязательные параметры - owner_id, item_id. Остальные
        добавятся в словарь параметров, если существуют.
        :return: {"response": 1}
        """

        sbis_id, vk_id = product_info['sbis_id'], product_info['vk_id']

        optional_params = ['name', 'description', 'category_id', 'price', 'old_price', 'url']

        logger.debug(f"Запускаю логику добавления товара")

        logger.debug("Формируем параметры запроса")
        # Обязательные значения
        data = {
            'owner_id': -VK_owner_id,
            'item_id': vk_id,
            'v': '5.199',
        }
        "Скачиваем фото"
        pic_urls = product_info.get('pic_urls')
        if pic_urls:
            pic_download(sbis_id, pic_urls)
            main_photo_path = self.media_dir / f"{sbis_id}-1.jpg"
            if not main_photo_path.is_file():
                logger.warning(f'изображения нет в каталоге ({main_photo_path}), пропускаем итерацию с товаром {sbis_id}')
            logger.debug("Добавляю фото товара")
            url = self.get_url(access_token)
            product_data = self.download_photo(url, photo_path=str(main_photo_path))
            photo_id = self.get_photo_id(product_data, access_token=access_token)
            logger.debug(f'photo_id - {photo_id}')

            if photo_id:
                data['main_photo_id'] = photo_id

        # Перебираем все варианты необязательных параметров, смотрим есть ли они среди переданных параметров
        for param in optional_params:
            item_param = product_info.get(param)
            if item_param:
                data[param] = item_param
        logger.debug(f"Сформировал параметры запроса - {data}")

        response = requests.post('https://api.vk.com/method/market.edit', data=data).json()
        logger.info(response)
        time.sleep(1)
        if response.get('response'):
            return response['response']['market_item_id']

    def sync_one_prod(self, auth_code, product_data):
        sbis_id = product_data['sbis_id']
        pic_urls = product_data['pic_urls']
        vk_category_id = product_data['vk_category_id']
        name = product_data['name']
        desc = product_data['desc']
        site_link = product_data['site_link']
        price = product_data['price']
        old_price = product_data['old_price']

        "получаем access_token"
        access_token = self.auth(auth_code)
        if not access_token:
            logger.error("Не удалось получить access_token")
            return None

        "Скачиваем фото"
        logger.debug(f"Запускаю логику добавления товара")
        pic_download(sbis_id, pic_urls)
        main_photo_path = self.media_dir / f"{sbis_id}-1.jpg"
        if not main_photo_path.is_file():
            logger.warning(f'изображения нет в каталоге ({main_photo_path}), пропускаем итерацию с товаром {name}')
            return 'изображения нет в каталоге'

        url = self.get_url(access_token)
        product_data = self.download_photo(url, photo_path=str(main_photo_path))
        photo_id = self.get_photo_id(product_data, access_token=access_token)
        prod_vk_id = self.add_product(vk_category_id, photo_id, name=name, desc=desc, site_link=site_link,
                                      price=price, access_token=access_token)
        return prod_vk_id


if __name__ == "__main__":
    PI = ProductIntegrations()
    products = PI.get_products('vk2.a.Y0dg84LxL98P7yf44x0V1Z5BdtMYsUbKZzGiMDosA0h_t-a-bXp4gyF4LNkXVtlPpX3255dfjFE0Yl4IiaYKqgPpI0ck8ygSBEluOBatHnCLqvPs9MW8tmfwwZ1cIXpaUucwgvZ5_1xfTXuFtQMgzjmbGPMRH8AO6XzPuVd9Dkz_xLlfY_FxRlqzh2WgiDLrNtLbDUNk21r2OvEv7BKo8jrAQZ443waT5SGDuwEvCac')
    print(products)
