import requests
import time
import json
import aiohttp
import asyncio
from pathlib import Path

from sql_magic import PgSqlModel
from YP.logger import logger
from get_from_unisiter import get_product_link
from utilits import strip_tags


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
