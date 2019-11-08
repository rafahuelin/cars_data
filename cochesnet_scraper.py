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
from config import car_columns, ublock, nordvpn, today, current_year

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

locale.setlocale(locale.LC_TIME, '')


class CochesNetCarScraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.install_addon(nordvpn)
        self.driver.implicitly_wait(50)
        self.last_visited = 1
        self.limit_pages = 3
        self.engine = create_engine('sqlite:///cars_data.db')
        self.df = self.load_or_create_db('cars_cochesnet')
        self.prov_df = self.load_or_create_db('zip_codes')

    def start(self):
        print(self.df)
        self.driver.get('https://www.coches.net/')
        # # # # self.driver.install_addon(ublock)
    #     self.driver.minimize_window()
    #     self.driver.maximize_window()
    #     time.sleep(10)
    #     privacy_policy_btn = self.driver.find_element_by_xpath("//div[@class='sui-CmpUi-actions']/button[2]")
    #     self.driver.find_element_by_xpath("//a[@href='/segunda-mano/']/").click()
    #     privacy_policy_btn.click()
    #     self.loop_cards()

    # def loop_cards(self):
    #     cards_container = self.driver.find_element_by_xpath("//div[@class='mt-SerpList']")
    #     cars_list = cards_container.find_elements_by_xpath("//div[@class='mt-SerpList-item']")
    #     for i, car in enumerate(cars_list):
    #         print(f"=== {len(cars_list)} - {i} ===")
    #         row = {}
    #         print('1[***]')
    #         item_id = car.get_attribute('id')
    #         print('2[***]')
    #         if self.is_already_in_db(item_id):
    #             print("Car already in Database")
    #             continue
    #         print('3[***]')
    #         row['Item Id'] = item_id
    #         time.sleep(random.uniform(4, 7))
    #         try:
    #             car.click()
    #         except ElementNotInteractableException:
    #             continue
    #         except ElementClickInterceptedException:
    #             element = self.driver.find_element_by_xpath("//*[contains(@class, 'QuickFiltersBar__filters QuickFiltersBar__filters--secondary']")
    #             self.driver.execute_script("arguments[0].click();", element)
    #         row['Price'] = car.find_element_by_xpath("//div[@class='mt-AdPrice-amount')]/strong[contains(text(),' €')]")
    #         print(row['Price'], '<-------')
            # # # self.get_or_empty("//div[@class='mt-AdPrice-amount')]/strong[contains(text(),' €')]").text
        #     print('4[***]')
        #     self.driver.switch_to.window(self.driver.window_handles[-1])
        #     print('5[***]')
        #     main_error = self.get_or_empty("//div[contains(@class, 'container-main-error')]")
        #     if main_error:
        #         continue
        #     print('6[***]')
        #     url = self.driver.current_url
        #     print('7[***]')
        #     row['Url'] = url
        #     print('8[***]')
        #     row['Url Id'] = url.split('-')[-1]
        #     print('9[***]')
        #     time.sleep(random.uniform(4, 7))
        #     row['Manufacturer'] = self.get_or_empty("//*[text()='Marca']/following-sibling::*")
        #     print('10[***]')
        #     row['Model'] = self.get_or_empty("//*[text()='Modelo']/following-sibling::*")
        #     print('11[***]')
        #     row['Year'] = self.get_or_empty("//*[text()='Año']/following-sibling::*")
        #     print('12[***]')
        #     row['Mileage'] = self.get_or_empty("//*[text()='Kilómetros']/following-sibling::*")
        #     print('13[***]')

        #     print('14[***]')
        #     row['Fuel'] = self.get_or_empty("//i[contains(@class, 'ico-car') and contains(@class, 'engine')]/following-sibling::*")
        #     print('15[***]')
        #     row['Gear'] = self.get_or_empty("//i[contains(@class, 'ico-car') and contains(@class, 'gear')]/following-sibling::*")
        #     print('16[***]')
        #     row['Doors'] = self.get_or_empty("//i[contains(@class, 'ico-car') and contains(@class, 'door')]/following-sibling::*")
        #     print('17[***]')
        #     row['Seats'] = self.get_or_empty("//i[contains(@class, 'ico-car_seats')]/following-sibling::*")
        #     row['City'] = self.get_or_empty("//i[contains(@class, 'ico-distance_grey_mobile')]/following-sibling::*")
        #     zip_code = self.get_or_empty("//i[contains(@class, 'ico-distance_grey_mobile')]/..").split(',')[0]
        #     print('18[***]')
        #     row['Zip Code'] = zip_code
        #     row['Province'] = self.get_province(zip_code)
        #     print('19[***]')
        #     row['Scraping Date'] = today
        #     # raw_post_date = self.driver.find_element_by_xpath("//div[@class='card-product-detail-user-stats-published']")
        #     raw_post_date = self.get_or_empty("//div[@class='card-product-detail-user-stats-published']")
        #     row['Posted Date'] = self.raw_to_date(raw_post_date)
        #     print(row['Scraping Date'], row['Posted Date'])
        #     print('20[***]')
        #     self.df = self.df.append(row, ignore_index=True)
        #     print('21[***]')
        #     self.driver.close()
        #     self.driver.switch_to.window(self.driver.window_handles[0])
        #     print(row.values())
        #     self.df.to_sql('cars', self.engine, if_exists='replace', index=False)
        # self.driver.quit()

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
            year_tail = f'-{current_year}'
            new_year_tail = f'.{year_tail}'
            # print(raw_date, raw_date.text, type(raw_date))
            # str_date = raw_date.text.replace(year_tail, new_year_tail)
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


cochesnet_scraper = CochesNetCarScraper()
cochesnet_scraper.start()
