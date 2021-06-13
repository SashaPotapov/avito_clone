from _typeshed import NoneType
import requests
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
from random import randrange

from app import create_app
from app.models import Role, db, Product, User
from format_published import format_published


logging.basicConfig(filename='parser.log', level=logging.INFO)

headers = {
    "Accept":  "*/*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
}


def get_html(page=1):
    '''Функция get_html возвращает первую страницу, если не возникает сетевых ошибок'''
    try:
        url = f"https://www.avito.ru/moskva/planshety_i_elektronnye_knigi/elektronnye_knigi-ASgBAgICAUSYAohO?cd=1&p={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    except(ConnectionError, requests.RequestException, ValueError):
        logging.error(f'Ошибка get_html {response.status_code}')
        return False

    except Exception as er:
        logging.error(f'Ошибка get_html {er}')
        return False


def get_products_links():
    '''Функция get_products_links возвращает список ссылок на все товары категории'''
    main_page = get_html()
    if main_page:
        soup = BeautifulSoup(main_page, 'lxml')
        # Определяет количество страниц товаров данной категории
        try:
            count_pages = int(soup.find('div', class_="pagination-root-2oCjZ").find_all('span', class_="pagination-item-1WyVp")[-2].text)
        except AttributeError:
            end_page = 1

        if count_pages > 5:
            end_page = 5
        else:
            end_page = count_pages

        logging.info(f'{end_page} страниц для парсинга')
        links = []
        pages_gen = range(1, end_page + 1)
        for p in pages_gen:
            page = get_html(p)
            soup = BeautifulSoup(page, 'lxml')
            item_card = soup.find_all('div', class_="iva-item-content-m2FiN")
            for item in item_card:
                link = f"https://www.avito.ru{item.find('div', class_='iva-item-titleStep-2bjuh').find('a').get('href')}"
                links.append(link)
            logging.info(f'{p} страницы спарсированны продукты')
        logging.info(f'{len(links)} продуктов найдено')
        return links
    return False


def get_product_html():
    '''Функция get_product_html возвращает список html-страниц по каждому товару категории'''
    links = get_products_links()
    if links:
        html_of_products = []
        for link_num, link in enumerate(links):
            try:
                response = requests.get(link, headers=headers)
                response.raise_for_status()
            except(requests.RequestException, ValueError):
                logging.error(f'Ошибка get_product_html {response.status_code}')
                continue
            except Exception as er:
                logging.error(f'Ошибка get_product_html {er}')
                continue
            html_of_products.append(response.text)
            logging.info(f'{link_num+1} {link} ссылка на продукт спарсирована')
            sleep(10)
        return html_of_products
    return False


def get_product_info():
    '''Функция get_product_info выводит информацию по каждому товару'''
    html_of_products = get_product_html()
    if html_of_products:
        for html_num, html in enumerate(html_of_products):
            soup = BeautifulSoup(html, 'lxml')

            # Использую regex для того чтобы найти id
            avito_user_id_regex = re.compile(r'((profile\?id=)|(shopId=))(\d+)&')
            avito_user_id_url = soup.find('div', class_="seller-info-name js-seller-info-name").find('a')['href']
            logging.info(avito_user_id_url)
            avito_user_id = avito_user_id_regex.search(avito_user_id_url).group(4)

            avito_user_name = soup.find('div', class_="seller-info-name js-seller-info-name").find('a').text.strip()

            title = soup.find('div', class_="item-view-content").find('span', class_="title-info-title-text").text.strip()
            avito_id = soup.find('div', class_="item-view-content-right").find('div', class_="item-view-search-info-redesign").find('span').text.strip()[2:]

            published = soup.find('div', class_="title-info-actions").find('div', class_="title-info-metadata-item-redesign").text.strip()
            published = format_published(published)

            link_photo = soup.find('div', class_="item-view-content").find('div', class_="gallery-img-frame js-gallery-img-frame").get('data-url').strip()

            try:
                price = soup.find('div', class_="item-view-content-right").find('span', class_="js-item-price").text.strip()
            except AttributeError:
                price = 0
                
            category = soup.find('div', class_="item-navigation").find_all('span', itemprop="itemListElement")[-1].find('span').text.strip()
            try:
                address = soup.find('div', class_="item-view-block item-view-map js-item-view-map").find('span', class_="item-address__string").text.strip()
            except AttributeError:
                address = '' 
            try:
                description = soup.find('div', class_="item-description").text.strip()
            except AttributeError:
                description = ''
            
            logging.info(f'{html_num+1} данные продукта получены')

            save_user_info(avito_user_id, avito_user_name, address)
            save_product_info(title, avito_id, published, link_photo, address, price, description, category, avito_user_id)

        logging.info(f'Все данные получены')
        return

    logging.error('get_product_info ошибка работы парсера')
    return None
    

def save_user_info(avito_user_id, avito_user_name, address):
    '''Функция save_product_info сохраняет инфо юзера в бд'''
    user_exists = User.query.filter(User.username == avito_user_id).count()

    if not user_exists:
        user = User(username=avito_user_id, email=f'{avito_user_id}@avito', name=avito_user_name, date_birth=datetime(1900, 1, 1), address=address,\
                    role_id=Role.query.filter_by(name='AvitoUser').first().id)
        db.session.add(user)
        db.session.commit()
        return
    logging.info('Данные юзера уже есть в бд')

def save_product_info(title, avito_id, published, link_photo, address, price, description, category, avito_user_id):
    '''Функция save_product_info сохраняет инфо продукта в бд'''
    product_exists = Product.query.filter(Product.avito_id == avito_id).count()
    
    if not product_exists:
        product = Product(title=title, avito_id=avito_id, published=published, link_photo=link_photo, address=address, price=price,\
                            description=description, category=category, user_id=User.query.filter_by(username=avito_user_id).first().id)
        db.session.add(product)
        db.session.commit()
        return
    logging.info('Данные продукта уже есть в бд')

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        get_product_info()
