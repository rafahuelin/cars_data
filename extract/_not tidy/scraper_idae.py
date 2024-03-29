# import numpy as np
import pandas as pd
import datetime
import locale
import os
import random
import sys
import time
import winsound
from sqlalchemy import create_engine
from sqlite3 import OperationalError
from config import idae_car_columns, ublock, today, current_year

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

locale.setlocale(locale.LC_TIME, '')


class IdaeCarScraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.install_addon(ublock)
        self.driver.implicitly_wait(1)
        self.current_page = 193
        self.engine = create_engine('sqlite:///idae.db')
        self.df = self.load_or_create_db('cars')
        self.small_pause = 0.5

    def start(self):
        print(self.df)
        self.driver.get('http://coches.idae.es/base-datos/marca-y-modelo')
        self.driver.minimize_window()
        self.driver.maximize_window()
        time.sleep(7)
        search_btn = self.driver.find_element_by_xpath("//i[@class='fas fa-search']/..")
        search_btn.click()
        pp_100 = self.driver.find_element_by_xpath("//select[@name='datos_nedc_length']/option[@value='100']")
        pp_100.click()
        while not self.driver.find_elements_by_xpath(f"//li[@class='paginate_button page-item active']/a[text()={self.current_page}]"):
            time.sleep(self.small_pause)
            next_button = self.driver.find_element_by_xpath("//li[@id='datos_nedc_next']/a")
            next_button.click()
        self.loop_pages()

    def loop_pages(self):
        while True:
            # self.save_page()
            for i in range(2):
                self.driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
                time.sleep(self.small_pause)
            disabled_next_button = self.get_or_empty("//li[@id='datos_nedc_next' and contains(@class, 'disabled')]")

            table_cars = self.driver.find_elements_by_xpath("//table[@id='datos_nedc']/tbody/tr/td/a")
            self.loop_cars(table_cars)
            next_button = self.driver.find_element_by_xpath("//li[@id='datos_nedc_next']/a")
            next_button.click()
            time.sleep(self.small_pause * 2)
            self.current_page += 1
            self.export_last_page()

    def loop_cars(self, table_cars):
        for i, car in enumerate(table_cars):
            print(f"=== Page: {self.current_page} - Item: {i} ===")
            row = {}
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(self.small_pause)
            try:
                car.click()
            except ElementClickInterceptedException:
                self.beep()
                # self.driver.quit()
                # self.start()

            time.sleep(self.small_pause * 2)
            for prop in idae_car_columns:
                try:
                    prop_details = self.driver.find_element_by_xpath(f"//td[contains(text(), '{prop}')]/following-sibling::*").text
                    row[prop] = prop_details
                except StaleElementReferenceException:
                    row[prop] = None
                # print(prop, prop_details)
            energy_classification = self.driver.find_element_by_xpath(f"//td[contains(text(), 'Clasificación por Consumo Relativo')]/following-sibling::*/img").get_attribute('title')
            row['Clasificación por Consumo Relativo'] = energy_classification
            print('Clasificación por Consumo Relativo', energy_classification)
            # self.driver.find_element_by_tag_name("//i[@class='far fa-window-close']/..").click()
            for i in range(2):
                time.sleep(self.small_pause)
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
            time.sleep(self.small_pause)
            self.df = self.df.append(row, ignore_index=True)
            self.df.to_sql('cars', self.engine, if_exists='replace', index=False)

    def beep(self):
        frequency = 2500  # Set Frequency To 2500 Hertz
        duration = 1000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)

    def export_last_page(self):
        with open('page.txt', 'w') as file:
            file.write(str(self.current_page))

    def is_already_in_db(self, item_id):
        item_in_db = not self.df[self.df['Item Id'] == item_id].empty
        return item_in_db

    def get_or_empty(self, xpath_arg):
        try:
            result = self.driver.find_element_by_xpath(xpath_arg).text
        except NoSuchElementException:
            result = ''
        # except InvalidSelectorException:
        #     result = None
        return result

    def load_or_create_db(self, table):
        if os.path.isfile('idae.db') and self.engine.has_table(table):
            df = pd.read_sql(table, self.engine)
            print("====READ DB")
        else:
            df = pd.DataFrame(None, columns=idae_car_columns)
            df.to_sql(table, self.engine)
            print("====CREATE DB")
        return df


idae_scraper = IdaeCarScraper()
idae_scraper.start()
