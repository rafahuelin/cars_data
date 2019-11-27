import pandas as pd
import datetime
import os
import random
import sys
import time
from sqlalchemy import create_engine
from sqlite3 import OperationalError
from config import car_columns, ublock, today

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

engine = create_engine('sqlite:///cars_data.db')
df = pd.read_sql('cars', engine)
item_in_db = not df.loc[df['Item Id'] == 'nzx54lqg5e62'].empty

prov_df = pd.read_sql('zip_codes', engine)
province = prov_df.loc[prov_df['Postal_code'] == 25001]['Province'].values[0]

driver = webdriver.Firefox()
driver.install_addon(ublock)
driver.implicitly_wait(50)
more_click_times = 1
driver.get('https://es.wallapop.com/coches-segunda-mano')
# driver.get('https://es.wallapop.com/item/volkswagen-caravelle-2012-423735475')
time.sleep(6)
driver.find_element_by_xpath("//*[@class='qc-cmp-button']").click()
driver.find_element_by_xpath("//div[@class='QuickFilter QuickFilter__sort']").click()
driver.find_element_by_xpath("//label[@for='id-newest']").click()
driver.switch_to.window(driver.window_handles[-1])

cards_container = driver.find_element_by_xpath("//div[@id='main-search-container']")
cars_list = cards_container.find_elements_by_xpath("//div[contains(@class, 'card') and contains(@class, 'card-product') and contains(@class, 'card-big')]")
car = cars_list[0]
item_id = get_attribute_or_continue(car, 'itemid')
# driver.find_element_by_xpath("//div[@class='card-product-detail-user-stats-published']").click()
# raw_post_date = driver.find_element_by_xpath("//div[@class='card-product-detail-user-stats-published']")

def get_attribute_or_continue(self, car, attribute):
    try:
        result = car.get_attribute(attribute)
    except NoSuchElementException:
        result = None
    return result

def raw_to_date(raw_date):
    if raw_date:
        year_tail = f'-{current_year}'
        new_year_tail = f'.{year_tail}'
        # print(raw_date, raw_date.text, type(raw_date))
        str_date = raw_date.text.replace(year_tail, new_year_tail)
        # str_date = raw_date.replace(year_tail, new_year_tail)
        date_format = datetime.datetime.strptime(str_date, "%d-%b-%Y")
    else:
        date_format = None
    return date_format


row = {
    'Item Id': '0a0a0a0a',
    'Url Id': 'www0a0a',
    'Manufacturer': 'Ferrari',
    'Model': 'Testarossa',
    'Price': '1.000.000 €',
    'Financed Price': '',
    'Mileage': 15,
    'Year': 2020,
    'Fuel': 'Gasolina',
    'Gear': 'Automático',
    'Doors': 3,
    'Seats': 2,
    'Province': 'Lleida',
    'City': 'Lleida',
    'Zip Code': 25001,
    'Warranty': '',
    'Posted Date': '2019-11-02',
    'Scraping Date': '2019-11-02',
    'Url': 'its.me'
}
df.drop(df.tail(1).index, inplace=True)

df = df.append(row, ignore_index=True)
df.to_sql('cars', engine, if_exists='replace', index=False)

df = pd.read_sql('cars', engine)

df.at[7,'Url']  # row and column
df.loc[7, 'Url']  # row and column
df.loc[df['Url'] == 'its.me', 'Url']
df.loc[df['Url'] == 'its.me', 'Url'].values[0]