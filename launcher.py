import os
import re
import time


def seconds_since_modified():
    mod_time = os.path.getmtime('idae.db')
    current_time = time.time()
    seconds_since_mod = current_time - mod_time
    return seconds_since_mod


def last_page():
    with open('page.txt', 'r') as file:
        page = file.read()
        return page


def replace_page():
    with open('scraper_idae.py', 'r') as file:
        filedata = file.read()

    old_page = re.findall(r"(?<=self.current_page = ).+$", filedata, re.M)
    new_page = last_page()

    filedata = filedata.replace(f'self.current_page = {old_page}', f'self.current_page = {new_page}')

    with open('scraper_idae.py', 'w') as file:
        file.write(filedata)


while True:
    seconds_since_mod = seconds_since_modified()
    if seconds_since_mod > 150:
        replace_page()
        os.system('python scraper_idae.py')
    time.sleep(2)
