# import numpy as np
import pandas as pd
import datetime
import locale
import os
import random
import sys
import time
from sqlalchemy import create_engine
from sqlite3 import OperationalError
from config import car_columns, ublock, today, current_year

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

locale.setlocale(locale.LC_TIME, '')


class WallapopCarScraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.install_addon(ublock)
        self.driver.implicitly_wait(65)
        self.more_click_times = 7
        self.engine = create_engine('sqlite:///cars_data.db')
        self.df = self.load_or_create_db('cars')
        self.prov_df = self.load_or_create_db('zip_codes')

    def start(self):
        print(self.df)
        self.driver.get('https://es.wallapop.com/coches-segunda-mano')
        self.driver.minimize_window()
        self.driver.maximize_window()
        time.sleep(10)
        self.driver.find_element_by_xpath("//*[@class='qc-cmp-button']").click()
        self.driver.find_element_by_xpath("//div[@class='QuickFilter QuickFilter__sort']").click()
        self.driver.find_element_by_xpath("//label[@for='id-newest']").click()
        time.sleep(8)
        self.driver.find_element_by_xpath("//*[contains(text(),'Ver más productos')]").click()
        for i in range(self.more_click_times):
            time.sleep(random.uniform(4,7))
            self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
        self.loop_cards()

    def loop_cards(self):
        try:
            cards_container = self.driver.find_element_by_xpath("//div[@id='main-search-container']")
        except NoSuchElementException:
            cards_container = self.driver.find_element_by_xpath("//div[@class='right-col']")
        cars_list = cards_container.find_elements_by_xpath("//div[contains(@class, 'card') and contains(@class, 'card-product') and contains(@class, 'card-big')]")
        for i, car in enumerate(cars_list):
            print(f"=== {len(cars_list)} - {i} ===")
            row = {}
            print('1[***]')
            item_id = self.get_attribute_or_continue(car, 'itemid')
            if not item_id:
                print("Not itemid")
                continue
            elif self.is_already_in_db(item_id):
                print("Car already in Database")
                continue
            print('2[***]')
            row['Item Id'] = item_id
            time.sleep(random.uniform(4, 7))
            try:
                car.click()
            except ElementNotInteractableException:
                continue
            except ElementClickInterceptedException:
                element = self.driver.find_element_by_xpath("//*[contains(@class, 'QuickFiltersBar__filters QuickFiltersBar__filters--secondary']")
                self.driver.execute_script("arguments[0].click();", element)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print('3[***]')
            main_error = self.get_or_empty("//div[contains(@class, 'container-main-error')]")
            if main_error:
                continue
            url = self.driver.current_url
            row['Url'] = url
            row['Url Id'] = url.split('-')[-1]
            time.sleep(random.uniform(3, 5))
            row['Manufacturer'] = self.get_or_empty("//*[text()='Marca']/following-sibling::*")
            row['Model'] = self.get_or_empty("//*[text()='Modelo']/following-sibling::*")
            row['Year'] = self.get_or_empty("//*[text()='Año']/following-sibling::*")
            row['Mileage'] = self.get_or_empty("//*[text()='Kilómetros']/following-sibling::*")
            row['Price'] = self.get_or_empty("//span[contains(@class, 'price') and contains(text(),' €')][1]")
            row['Fuel'] = self.get_or_empty("//i[contains(@class, 'ico-car') and contains(@class, 'engine')]/following-sibling::*")
            row['Gear'] = self.get_or_empty("//i[contains(@class, 'ico-car') and contains(@class, 'gear')]/following-sibling::*")
            row['Doors'] = self.get_or_empty("//i[contains(@class, 'ico-car') and contains(@class, 'door')]/following-sibling::*")
            row['Seats'] = self.get_or_empty("//i[contains(@class, 'ico-car_seats')]/following-sibling::*")
            row['City'] = self.get_or_empty("//i[contains(@class, 'ico-distance_grey_mobile')]/following-sibling::*")
            zip_code = self.get_or_empty("//i[contains(@class, 'ico-distance_grey_mobile')]/..").split(',')[0]
            row['Zip Code'] = zip_code
            row['Province'] = self.get_province(zip_code)
            row['Scraping Date'] = today
            raw_post_date = self.get_or_empty("//div[@class='card-product-detail-user-stats-published']")
            row['Posted Date'] = self.raw_to_date(raw_post_date)
            print(row['Scraping Date'], row['Posted Date'])
            self.df = self.df.append(row, ignore_index=True)
            print('4[***]')
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            print(row.values())
            self.df.to_sql('cars', self.engine, if_exists='replace', index=False)
        self.driver.quit()

    def get_attribute_or_continue(self, car, attribute):
        try:
            result = car.get_attribute(attribute)
        except NoSuchElementException:
            result = None
        return result

    def is_already_in_db(self, item_id):
        item_in_db = not self.df[self.df['Item Id'] == item_id].empty
        return item_in_db

    def get_province(self, zip_code):
        if zip_code:
            province = self.prov_df.loc[self.prov_df['Postal_code'] == int(zip_code)]['Province'].values[0]
        else:
            province = None
        return province

    def raw_to_date(self, raw_date):
        if raw_date:
            date_year = raw_date.split('-')[-1]
            year_tail = f'-{date_year}'
            new_year_tail = f'.{year_tail}'
            str_date = raw_date.replace(year_tail, new_year_tail)
            date_format = datetime.datetime.strptime(str_date, "%d-%b-%Y").date()
        else:
            date_format = None
        return date_format

    def get_or_empty(self, xpath_arg):
        try:
            result = self.driver.find_element_by_xpath(xpath_arg).text
        except NoSuchElementException:
            result = ''
        return result

    def load_or_create_db(self, table):
        if os.path.isfile('cars_data.db') and self.engine.has_table(table):
            df = pd.read_sql(table, self.engine)
            print("====READ DB")
        else:
            df = pd.DataFrame(None, columns=car_columns)
            df.to_sql(table, self.engine)
            print("====CREATE DB")
        return df


walla_scraper = WallapopCarScraper()
walla_scraper.start()
