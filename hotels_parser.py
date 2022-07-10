import os
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json


#driver = webdriver.Chrome("D:\PythonProg\PycharmProjects\ParcingLearning\chrome_driver\chromedriver.exe")
hotels_url = "https://www.tury.ru/hotel/"


def get_page_with_selenium(url, file_name):
    try:
        driver.get(url)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_hotels_categories(html_page, out_file):
    with open(html_page, encoding="utf-8") as html_file:
        src = html_file.read()

    soup = BeautifulSoup(src, "lxml")
    list = soup.find("div", class_="best_hotels").find("ul").find_all("a")
    hotels_categories = [f"https://www.tury.ru/{tag.get('href')}" for tag in list]

    with open(out_file, "w") as file:
        for category in hotels_categories:
            print(category, file=file)


def get_category_page(cat_url, close=True):
    try:
        driver.get(cat_url)
        time.sleep(10)
        with open(f'hotels_data/{create_filename(cat_url)}.html', "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        print(f"File {create_filename(cat_url)}.html was created")
    except Exception as ex:
        print(ex)
    finally:
        if close:
            driver.close()
            driver.quit()


def get_categories(file_name):
    with open(file_name, "r") as file:
        for cat_url in file:
            get_category_page(cat_url.strip(), close=False)
        driver.close()
        driver.quit()


def create_filename(cat_url):
    s = cat_url[::-1]
    start_index = s.find(".")
    end_index = s.find("/")
    s = s[start_index+1:end_index]
    return s[::-1]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_category(cat_page):
    with open(cat_page, "r", encoding="utf-8") as html_file:
        src = html_file.read()

    soup = BeautifulSoup(src, "lxml")
    hotels = soup.find_all("div", class_="hotel_card_dv")
    hotel_data = {"name": "", "location": "", "rate": 0}
    hotels_data = []

    for hotel in hotels:
        hotel_data = {"name": "", "location": "", "rate": 0}

        name = hotel.find(class_="hotel_name").text.strip()
        location = f"{hotel.find(class_='resort loc').text.strip()}, {hotel.find(class_='country loc').text.strip()}"
        rate = hotel.find(class_="rsrvme_hc_hotel_links").find("li").text.strip()

        hotel_data["name"] = name
        hotel_data["location"] = location
        if is_number(rate):
            hotel_data["rate"] = rate
        else:
            hotel_data["rate"] = "Undefined"

        hotels_data.append(hotel_data)
        #print(hotel_data)

    return hotels_data



def parse_to_json(dir_path, json_file):
    hotels_info = []

    for file in os.listdir(dir_path):
        hotel_info = parse_category(f"{dir_path}/{file}")
        hotels_info.extend(hotel_info)

    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(hotels_info, file, indent=4, ensure_ascii=False)


# parse_to_json("D:\PythonProg\PycharmProjects\ParcingLearning\hotels_data", "Hotels.json")

