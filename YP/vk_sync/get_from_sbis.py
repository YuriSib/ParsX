import requests
import time
import json
import aiohttp
import asyncio
from pathlib import Path

from .models import Products

from YP.logger import logger
from .get_from_unisiter import get_product_link
from .utilits import strip_tags


SBIS_TOKEN = "rbbew4LZMbof6GNJEWy0ZAz8jRhS3qQRaMLuiWQbcNHUyfj2WCpOswpo86FJyKoEKIT2Rqmmzufc3YHMdp8ZggucdnWRQTvQ56fMP4RW1pHsbwVUxwyZv3"
SBIS_PRICE_ID = 205
headers_ = {"X-SBISAccessToken": SBIS_TOKEN}


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

            response = requests.get(url, headers=headers_)
            with open(file_path, 'wb') as file:
                file.write(response.content)
                cnt_img += 1


def get_products(price, point_id):
    page = 0
    nomenclatures = []
    while True:
        parameters = {
            'pointId': point_id,
            'priceListId': price,
            'withBalance': 'true',
            'withBarcode': 'false',
            'page': page,
            'pageSize': '2000'
        }
        url = 'https://api.sbis.ru/retail/nomenclature/list?'

        response = requests.get(url=url, params=parameters, headers=headers_).json()
        nomenclatures.extend(response['nomenclatures'])

        if response['outcome']['hasMore']:
            logger.info(f'Получил ответ по странице №{page}')
            page += 1
            # logger.warning('Работа фунцкии прекращена досрочно')
            # return nomenclatures
        else:
            return nomenclatures


def get_item_list(point_id=None):
    "Получает список товаров и категорий СБИС"
    prices_list = [SBIS_PRICE_ID]

    responses = []
    for price in prices_list:
        if point_id:
            response = get_products(price, point_id)
            responses.append(response)

    nomenclatures = []
    for response in responses:
        nomenclatures.extend(response)

    category_list, product_list = [], []
    for product in nomenclatures:
        if product["isParent"]:
            category_list.append((product["hierarchicalId"], product["hierarchicalParent"], product["name"]))
        elif not product["isParent"]:
            product_list.append(({
                'sbis_id': product['nomNumber'],
                'name': product['name'],
                'description': product['description'],
                'parameters': product['attributes'],
                'images': product['images'],
                'price': product['cost'],
                'category': product['hierarchicalParent'],
                'stocks': product['balance']
            }))
    return category_list, product_list


def catalog_sync(customer_id):
    "Синхронизирует товары СБИС и БД"
    category_list, product_list = get_item_list()
    for product in product_list:
        parameters = json.dumps(product['parameters'])

        description = strip_tags(product['description']) if product['description'] else ''
        unisiter_url = get_product_link(product['name'])

        try:
            Products.objects.update_or_create(
                sbis_id=product['sbis_id'],
                defaults={
                    'customer_id': customer_id, 'name': product['name'], 'description': description,
                    'parameters': parameters, 'price': product['price'], 'images': product['images'],
                    'category_id': product['category'], 'stocks': product['stocks'], 'unisiter_url': unisiter_url
                }
            )
        except Exception as e:
            logger.error(f'Ошибка {e}')


# if __name__ == "__main__":
#     category_list, product_list = get_item_list()
#     print(category_list)
#     print(product_list)
