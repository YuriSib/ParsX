import requests
import time
import json
import aiohttp
import asyncio
from pathlib import Path
import traceback

from bulk_update_or_create import BulkUpdateOrCreateQuerySet

from .models import Products, Categories, Integrations
from YP.logger import logger
from .get_from_unisiter import get_product_link, get_price
from .utilits import strip_tags
from .sql_magic import upsert_products


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
    logger.debug(f"Пытаюсь получить товары от СБИС")
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
            logger.debug(f"Получено {len(nomenclatures)} товаров")
            return nomenclatures


def get_item_list(point_id=None):
    "Получает список товаров и категорий СБИС"
    prices_list = SBIS_PRICE_ID

    response = get_products(SBIS_PRICE_ID, point_id)

    nomenclatures = []
    nomenclatures.extend(response)

    category_list, product_list = [], []
    for product in nomenclatures:
        if product["isParent"]:
            category_list.append((product["hierarchicalId"], product["hierarchicalParent"], product["name"]))
        elif not product["isParent"]:
            # if product['name'] == "Грунт Живая земля универсал. 50л":
            #     logger.info(f"""При подтягивании из СБИС, товар "Грунт Живая земля универсал". 50л имеет цену {product['cost']  }""")
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
    logger.debag(f"catalog_sync вызван для customer_id={customer_id}")
    traceback.print_stack()
    logger.debug(f"Начинаю синхронизацию товаров СБИС и БД")
    category_list, product_list = get_item_list(334198)
    logger.debug(f"Извлечено {len(product_list)} товаров из {len(category_list)} категорий")

    product_objects = []
    for product in product_list:
        logger.debug(f"Обрабатываю {product['name']}")
        parameters = json.dumps(product['parameters'])

        description = strip_tags(product['description']) if product['description'] else ''
        unisiter_url = get_product_link(product['name'])

        old_price, price = None, None
        # if unisiter_url:
        #     old_price, price = get_price(f'https://polezniemelochi.ru{unisiter_url}')

        product_obj = {
            'sbis_id': product['sbis_id'],
            'customer_id': customer_id,
            'name': product['name'],
            'description': description,
            'parameters': parameters,
            'old_price': old_price,
            'price': price,
            'images': product['images'],
            'category_id': product['category'],
            'stocks_mol': product['stocks'],
            'unisiter_url': unisiter_url,
        }
        product_objects.append(product_obj)

    try:
        logger.debug(f'Запускаю upsert_products')
        upsert_products(product_objects)
        logger.debug(f'Функция upsert_products выполнена')
    except Exception as e:
        logger.error(f'Ошибка {e}')


# if __name__ == "__main__":
#     category_list, product_list = get_item_list()
#     print(category_list)
#     print(product_list)
