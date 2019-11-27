import numpy as np
import pandas as pd
import datetime
import os
import requests
import sys
import time
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlite3 import OperationalError


class CarsScraper:
    def __init__(self, initial_url):
        self.initial_url = initial_url
        self.headers = {'User-Agent': 'https://github.com/rafahuelin - Proyecto Datascience para Portfolio - rafahuelin@gmail.com'}
        self.engine = create_engine('sqlite:///cars_scraper.db')
        self.visited = []
        self.columns = [
            'Id',
            'Manufacturer',
            'Model',
            'Cash Price',
            'Financed Price',
            'Mileage',
            'Year',
            'Fuel',
            'City',
            'Warranty',
            'Posted Datetime',
            'Scraping Date',
            'Picture Url'
        ]
        self.df = self.load_or_create_db()
        self.load_url(initial_url)

    def load_or_create_db(self):
        self.engine = create_engine('sqlite:///cars_scraper.db')
        if os.path.isfile('cars_scraper.db'):
            df = pd.read_sql('cars', self.engine)
        else:
            df = pd.DataFrame(None, columns=self.columns)
            df.to_sql('cars', self.engine)
        return df

    def load_url(self, url):
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200:
            self.visited.append('url')
            soup = BeautifulSoup(res.text, 'html.parser')
            print("================", soup, "================")
            car_list = soup.find('div', {'id': 'v2'})
            print(car_list)
            self.get_details(car_list)
        return

    def get_details(self, car_list):
        for car in car_list.find_all('div', {'class': 'mt-SerpList-item'}):
            # prepare data
            title = car.find('h2', {'class': 'mt-CardAd-title'}).text.strip()
            attribute_list = car.find('ul', {'class': 'mt-CardAd-attributesList'})

            row = {}
            row['Id'] = car.get('id')

            row['Manufacturer'] = title.split(' ')[0]
            row['Model'] = ' '.join(title.split(' ')[1:])
            row['Cash Price'] = car.find('div', {'class': 'mt-AdPrice-amount'}).find('strong').text
            Financed_Price = car.find('div', {'class': 'mt-AdPrice-amount mt-AdPrice-amount--dark'})
            if Financed_Price:
                row['Financed Price'] = Financed_Price.find('strong').text
            else:
                row['Financed Price'] = ""

            row['Mileage'] = attribute_list.find_all('li')[3].text.strip()
            row['Year'] = attribute_list.find_all('li')[2].text.strip()
            row['Fuel'] = attribute_list.find_all('li')[1].text.strip()
            row['City'] = attribute_list.find_all('li')[0].text.strip()
            row['Picture Url'] = car.find('div', {'class': 'p preload j_photo'}).get('data-iurl')
            displayed_datetime = car.find('span', {'class': 'mt-CardAd-date'}).text.strip()

            row['Posted Datetime'] = self.get_datetime(displayed_datetime)
            self.df = self.df.append(row, ignore_index=True)
        self.df.to_sql('cars', self.engine)

    def get_datetime(self, displayed_datetime):
        if 'min.' in displayed_datetime:
            for t in displayed_datetime.split(' '):
                if t.isnumeric():
                    minutes = int(t)
                    posted_datetime = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        elif 'Hoy' in displayed_datetime:
            time_str = displayed_datetime.replace('Hoy ', '')
            hour, minutes = time_str.split(':')
            posted_datetime = datetime.now().replace(hour=hour, minutes=minutes)
            if datetime.datetime.now().hour > 12:
                posted_datetime = self.fix_datetime(posted_datetime)
        elif 'Ayer' in displayed_datetime:
            time_str = displayed_datetime.replace('Ayer ', '')
            hour, minutes = time_str.split(':')
            yesterday = datetime.now() - datetime.timedelta(days=1)
            day = yesterday.day
            posted_datetime = datetime.now().replace(days=day, hour=hour, minutes=minutes)
        elif '/' in displayed_datetime and ':' in displayed_datetime:
            date_str, time_str = displayed_datetime.split(' ')
            hour, minutes = time_str.split(':')
            day, month = date_str.split('/')
            posted_datetime = datetime.datetime.now().replace(month=month, day=day, hour=hour, minutes=minutes)
            posted_datetime = fix_datetime(posted_datetime)
        else:
            posted_datetime = None
        return posted_datetime

    def fix_datetime(posted_datetime):
        previous_datetime = self.df.tail(1)['Posted Datetime']
        posted_datetime = datetime.now().replace(hour=hour, minutes=minutes)
        if posted_datetime < previous_datetime:
            hour += 12
            posted_datetime.replace(hour=hour)

    def next_page(self):
        if self.visited[-1] == self.initial_url:
            next_url = self.initial_url + '?pg=2'
        else:
            previous_page = int(self.visited[-1].split['='][-1])
            next_page = str(previous_page + 1)
            if next_page > 10:
                sys.exit()
            next_url = self.initial_url + '?pg=' + next_page
        self.load_url(next_url)


scraper = CarsScraper('https://www.coches.net/segunda-mano/')


# if __name__ == '__main__':
#     pass
