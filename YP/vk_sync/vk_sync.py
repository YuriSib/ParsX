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

        logger.debug(f'refresh_token, device_id, state : {refresh_token, device_id, state}')
        logger.debug('Post-запрос для обмена access_token')
        logger.debug(f'url - {url}')
        logger.debug(f'headers - {headers}')
        logger.debug(f'data - {payload}')
        response = requests.post(url, data=payload, headers=headers).json()

        logger.debug(f"Ответ - {response}")
        try:
            refresh_token = response.get('refresh_token')
            access_token = response.get('access_token')
            logger.debug(f"refresh_token - {refresh_token}\n access_token - {access_token}")

            if refresh_token:
                logger.debug("Завершаю функцию get_access, возвращаю refresh_token и access_token")
                return refresh_token, access_token
        except Exception as e:
            logger.error(f'Ошибка при попытке получить ответ {e}')

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
    def add_product(category_id, main_photo_id, name, desc, site_link, price, access_token):
        price = str(price)
        data = {
            'owner_id': -VK_owner_id,
            'name': name,
            'description': desc,
            'category_id': category_id,
            'main_photo_id': main_photo_id,
            'access_token': access_token,
            'v': '5.199',
            'price': price,
        }

        if site_link:
            data['url'] = site_link

        response = requests.post('https://api.vk.com/method/market.add', data=data).json()
        logger.info(response)
        time.sleep(1)
        if response.get('response'):
            return response['response']['market_item_id']

    @staticmethod
    def get_products(access_token):
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

    def sync_one_prod(self, auth_code, product_data):
        sbis_id = product_data['sbis_id']
        pic_urls = product_data['pic_urls']
        vk_category_id = product_data['vk_category_id']
        name = product_data['name']
        desc = product_data['desc']
        site_link = product_data['site_link']
        price = product_data['price']

        "Загружаем товар в ВК"
        logger.debug('Получаю новый токен')
        tokens = Integrations.objects.get(authorization_code=auth_code)

        refresh_token, device_id, state = tokens.refresh_token, tokens.device_id, tokens.state

        token_data = self.get_access(refresh_token, device_id, state)
        logger.debug(f"token_data - {token_data}")
        if token_data:
            logger.debug(f"Пытаюсь извлечь токены из token_data...")
            try:
                new_refresh_token, access_token = token_data
            except Exception as E:
                logger.error(f"Не удалось извлечь данные, ошибка {E}")
            logger.debug(f"new_refresh_token -  {new_refresh_token}")
            try:
                tokens.refresh_token = new_refresh_token
                tokens.access_token = access_token
                tokens.save()
            except Exception as E:
                logger.error(f"Ошибка при обновлении токенов через djangoORM {E}")
                return None
        else:
            logger.error('Не удалось получить Токены')

        "Скачиваем фото"
        logger.debug(f"Запускаю логику добавления товара")
        pic_download(sbis_id, pic_urls)
        parent_dir = Path(__file__).resolve().parent
        media_dir = parent_dir / "media" / "products"
        main_photo_path = media_dir / f"{sbis_id}-1.jpg"
        if not main_photo_path.is_file():
            logger.warning(f'изображения нет в каталоге ({main_photo_path}), пропускаем итерацию с товаром {name}')
            return 'изображения нет в каталоге'

        url = self.get_url(access_token)
        product_data = self.download_photo(url, photo_path=str(main_photo_path))
        photo_id = self.get_photo_id(product_data, access_token=access_token)
        prod_vk_id = self.add_product(vk_category_id, photo_id, name=name, desc=desc, site_link=site_link,
                                      price=price, access_token=access_token)
        return prod_vk_id
