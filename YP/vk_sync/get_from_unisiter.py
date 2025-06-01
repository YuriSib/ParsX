import requests
import re
import time


def get_product_link(product_name):
    cookies = {
        'user_id': 'd405adc69302fa642e2e6da98ad0748c',
        'status_id': '1',
        '_ym_uid': '1721719735519807660',
        '_ym_d': '1737495251',
        'isCookieNotes': 'true',
        '_ym_isad': '1',
        'PHPSESSID': 'n6q73rea91hn95p5ke2181721k',
        '_ym_visorc': 'w',
    }
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'ru,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://polezniemelochi.ru',
        'priority': 'u=1, i',
        'referer': 'https://polezniemelochi.ru/',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "YaBrowser";v="25.4", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        # 'cookie': 'user_id=d405adc69302fa642e2e6da98ad0748c; status_id=1; _ym_uid=1721719735519807660; _ym_d=1737495251; isCookieNotes=true; _ym_isad=1; PHPSESSID=n6q73rea91hn95p5ke2181721k; _ym_visorc=w',
    }

    data = {
        'word': product_name,
    }

    response = requests.post(
        'https://polezniemelochi.ru/shop/search/ajax_search_hints.php',
        cookies=cookies,
        headers=headers,
        data=data,
    )
    time.sleep(1)

    match = re.search(r'<a\s+href="([^"]+)"', response.text)
    if match:
        return match.group(1)
    else:
        return 'Товар не найден'
