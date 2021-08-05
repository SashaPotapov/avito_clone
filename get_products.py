import logging
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

from app import create_app
from app.models import Product, Role, User, db
from format_published import format_published

logging.basicConfig(filename='parser.log', filemode='w', level=logging.INFO)

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
        + 'AppleWebKit/537.36 (KHTML, like Gecko) '
        + 'Chrome/90.0.4430.85 Safari/537.36'
    ),
}


def save_parsed_data():
    html_of_products = get_html_of_products()
    for html_num, html in enumerate(html_of_products):
        soup = BeautifulSoup(html, 'lxml')
        save_user_info(soup)
        save_product_info(soup)
        logging.info(f'{html_num+1} данные объявления получены')


def get_html_of_products():
    """Возвращает список html-страниц по каждому товару категории."""
    links = get_products_links()
    html_of_products = []
    for link_num, link in enumerate(links):
        try:
            response = requests.get(link, headers=headers)
        except requests.exceptions.RequestException as er:
            logging.error(f'Ошибка get_product_html {er}')
            raise er

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_er:
            logging.error(f'Ошибка get_product_html {http_er}')
            raise http_er

        html_of_products.append(response.text)
        logging.info(f'{link_num+1} {link} html страницы добавлен в список')
        sleep(9)
    return html_of_products


def get_products_links():
    """Возвращает список ссылок на все товары категории."""
    soup = BeautifulSoup(get_html(), 'lxml')
    links = []
    for page in range(1, get_end_page(soup) + 1):
        soup = BeautifulSoup(get_html(page), 'lxml')
        product_card = soup.find_all('div', class_='iva-item-content-m2FiN')
        for product in product_card:
            links.append(get_product_link(product))

        logging.info(f'{page}/{get_end_page(soup)} страниц обработаны')
    logging.info(f'{len(links)} объявлений найдено')
    return links


def get_html(page=1):
    """Возвращает html страницы, если не возникает сетевых ошибок."""
    url = (
        'https://www.avito.ru/moskva/planshety_i_elektronnye_knigi/'
        + f'elektronnye_knigi-ASgBAgICAUSYAohO?cd=1&p={page}'
    )

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as er:
        logging.error(f'Ошибка get_html {er}')
        raise er

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_er:
        logging.error(f'Ошибка get_html {http_er}')
        raise http_er

    return response.text


def get_end_page(soup):
    try:
        number_pages = int(
            soup.find(
                'div',
                class_='pagination-root-2oCjZ',
            ).find_all(
                'span',
                class_='pagination-item-1WyVp',
            )[-2].text,
        )
    except AttributeError:
        end_page = 1
        number_pages = end_page

    if number_pages > 5:
        end_page = 5
    else:
        end_page = number_pages

    logging.info(f'{end_page} страниц для парсинга')
    return end_page


def get_product_link(product):
    product_href = product.find(
        'div',
        class_='iva-item-titleStep-2bjuh',
    ).find('a').get('href')

    return (
        'https://www.avito.ru'
        + f'{product_href}'
    )


def save_user_info(soup):
    """Функция save_product_info сохраняет инфо юзера в бд"""
    email = f'{get_user_avito_id(soup)}@avito.ru'
    user_exists = User.query.filter(User.email == email).count()

    if not user_exists:
        user = User(
            email=email,
            name=get_user_name(soup),
            address=get_product_address(soup),
            role_id=Role.query.filter_by(name='AvitoUser').first().id,
        )
        db.session.add(user)
        db.session.commit()

    logging.info('Данные юзера уже есть в бд')


def get_user_avito_id(soup):
    avito_user_id_regex = re.compile(r'((profile\?id=)|(shopId=))(\d+)&')
    avito_user_id_url = soup.find(
        'div',
        class_='seller-info-name js-seller-info-name',
    ).find('a')['href']
    logging.info(avito_user_id_url)
    return avito_user_id_regex.search(avito_user_id_url).group(4)


def get_user_name(soup):
    return soup.find(
        'div',
        class_='seller-info-name js-seller-info-name',
    ).find('a').text.strip()


def save_product_info(soup):
    """Функция save_product_info сохраняет инфо продукта в бд"""
    product_exists = Product.query.filter(
        Product.avito_id == get_product_id(soup),
    ).count()

    if not product_exists:
        product = Product(
            title=get_product_title(soup),
            avito_id=get_product_id(soup),
            published=get_product_date(soup),
            link_photo=get_product_photo(soup),
            address=get_product_address(soup),
            price=get_product_price(soup),
            description=get_product_description(soup),
            category=get_product_category(soup),
            user_id=User.query.filter_by(
                email=f'{get_user_avito_id(soup)}@avito.ru',
            ).first().id,
        )
        db.session.add(product)
        db.session.commit()

    logging.info('Объявление уже есть в бд')


def get_product_title(soup):
    return soup.find(
        'div',
        class_='item-view-content',
    ).find(
        'span',
        class_='title-info-title-text',
    ).text.strip()


def get_product_id(soup):
    return soup.find(
        'div',
        class_='item-view-content-right',
    ).find(
        'div',
        class_='item-view-search-info-redesign',
    ).find('span').text.strip()[2:]


def get_product_date(soup):
    published = soup.find(
        'div',
        class_='title-info-actions',
    ).find(
        'div',
        class_='title-info-metadata-item-redesign',
    ).text.strip()
    return format_published(published)


def get_product_photo(soup):
    return soup.find(
        'div',
        class_='item-view-content',
    ).find(
        'div',
        class_='gallery-img-frame js-gallery-img-frame',
    ).get('data-url').strip()


def get_product_price(soup):
    try:
        price = soup.find(
            'div',
            class_='item-view-content-right',
        ).find(
            'span',
            class_='js-item-price',
        ).text.strip().split()
    except AttributeError:
        price = 0
    else:
        price = ''.join(price)
    return price


def get_product_category(soup):
    return soup.find(
        'div',
        class_='item-navigation',
    ).find_all(
        'span',
        itemprop='itemListElement',
    )[-1].find('span').text.strip()


def get_product_address(soup):
    try:
        address = soup.find(
            'div',
            class_='item-view-block item-view-map js-item-view-map',
        ).find(
            'span',
            class_='item-address__string',
        ).text.strip()
    except AttributeError:
        address = ''
    return address


def get_product_description(soup):
    try:
        description = soup.find(
            'div',
            class_='item-description',
        ).text.strip()
    except AttributeError:
        description = ''
    return description


if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        save_parsed_data()
