from bs4 import BeautifulSoup
import requests
import csv
import os
import io

#URL = 'https://auto.ru/sankt-peterburg/cars/saab/used/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36',
           'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

HOST = 'https://auto.ru/'

FILE = 'cars.csv'


def save_file(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Цена', 'Ссылка'])
        for item in items:
            writer.writerow([item['title'], item['price'], item['link']])


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('a', class_='Button Button_color_whiteHoverBlue Button_size_s Button_type_link Button_width_default ListingPagination-module__page')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='ListingItem-module__container')



    cars=[]
    for item in items:
        rub_price = item.find('div', class_='ListingItemPrice-module__content')
        if rub_price:
            rub_price.encoding = 'utf8'
            rub_price = rub_price.text.replace(u'\xa0','').replace(u'\u2009','')
        else:
            rub_price = 'Цену уточняйте'
        cars.append({
            'title': item.find('a', class_='ListingItemTitle-module__link').get_text(strip=True),
            'price': rub_price,
            'link': HOST + item.find('a', class_='Link ListingItemTitle-module__link').get('href')
        })

    return cars



def parse():
    URL = input('Введите ссылку URL: ')
    URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count+1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)}.')
        os.startfile(FILE)

    else:
        print('Error')

parse()