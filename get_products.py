import requests
import logging
from bs4 import BeautifulSoup


logging.basicConfig(filename='parser.log', level=logging.INFO)

def get_html():
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:89.0) Gecko/20100101 Firefox/89.0"
        }

        pages = []
        for i in range(1, 5):
            url = f"https://www.avito.ru/moskva/tovary_dlya_kompyutera/komplektuyuschie/protsessory-ASgBAgICAkTGB~pm7gniZw?cd=1&p={i}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            pages.append(response.text)
            return pages
    except(requests.RequestException, ValueError):
        logging.info(f'Ошибка {response.status_code}')
        return False
    except Exception as er:
        logging.info(er)
        return False
