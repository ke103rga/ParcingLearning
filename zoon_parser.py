from selenium import webdriver
from fp.fp import FreeProxy
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import requests
import re
import time


executable_path = "C:\\Users\\Виктория\\PycharmProjects\\UniversitiesParser\\chromedriver_win32\\chromedriver.exe"
test_url = "https://omsk.zoon.ru/beauty/"
site_home_url = "https://chelyabinsk.zoon.ru/"


def create_driver(exe_path=executable_path):
    proxy = FreeProxy(country_id=['RU'], rand=True).get()
    user_agent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"--proxy-server={proxy[proxy.index('//')+2:]}")
    options.add_argument(f"user-agent={user_agent.random}")
    driver = webdriver.Chrome(executable_path=exe_path, options=options)

    return driver


def get_cities(url, driver=None):
    if not driver:
        driver = create_driver()
    driver.get(url)
    city_selector = driver.find_element(By.CLASS_NAME, "header-city-select")
    city_selector.click()
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "lxml")

    cities_list = soup.find("ul", class_="header-city-select__suggest-results")
    cities = {li.get("data-name"): li.find("a").get("href") for li in cities_list.find_all("li")}

    driver.quit()
    driver.close()

    return cities


def get_categories(city_link, driver=None):
    if not driver:
        driver = create_driver()

    driver.get(city_link)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")

    categories_list = soup.find("ul", class_="new-index-nav__slider-items nav-categories")\
        .find_all("li", class_="nav-categories__item")
    categories = {}
    for li in categories_list:
        link = li.find("a")
        if link:
            print(link)
            categories[link.find("div", class_="nav").find_next("div").tetx.strip()] = link.get("href")

    driver.quit()
    driver.close()

    return categories


def get_whole_page(url, driver=None, download_file=None):
    if not driver:
        driver = create_driver()

    driver.get(url)
    time.sleep(10)

    ratio_list = driver.find_element(By.CLASS_NAME, "btop")
    cards = driver.find_element(By.CLASS_NAME, "service-items-medium")
    last_card = cards.find_elements(By.CSS_SELECTOR, ".minicard-item.js-results-item")[-1]

    while True:
        actions = ActionChains(driver)
        actions.move_to_element(ratio_list).perform()
        time.sleep(10)
        cards = driver.find_element(By.CLASS_NAME, "service-items-medium")
        if cards.find_elements(By.TAG_NAME, "li")[-1] == last_card:
            break
        else:
            last_card = cards.find_elements(By.TAG_NAME, "li")[-1]

    if download_file:
        with open(download_file, "w", encoding="utf-8") as file:
            file.write(driver.page_source)

    driver.quit()
    driver.close()

    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


def get_all_institutions(soup, file_name=None):
    cards = soup.find_all(class_="minicard-item js-results-item")
    if file_name:
        with open(file_name, "w") as file:
            for card in cards:
                link = card.find("h2", class_="minicard-item__title").find("a").get("href")
                print(link.strip(), file=file)

    else:
        links = list(map(lambda card: card.find("h2", class_="minicard-item__title").find("a").get("href"), cards))
        return links
    print("All links was successfully saved.")


def get_institution_data(url):

    def clean_text(text):
        text =  text.replace("\xa0", " ")
        return text.replace("&nbsp;", "")

    def get_number(link):
        pattern = "tel:"
        return link.replace(pattern, "")

    institution_data = {"name": "",
                        "address": "",
                        "phone_numbers": [],
                        "social_networks":[]}

    q = requests.get(url)
    soup = BeautifulSoup(q.content, "lxml")

    # with open("clinik.html", "r", encoding="utf-8") as file:
    #     soup = BeautifulSoup(file.read(), "lxml") # For debug

    institution_data["name"] = clean_text(soup.find("h1", class_="service-page-header--text").text.strip())
    institution_data["address"] = clean_text(soup.find("address").text)

    phones_list = soup.find(class_="service-phones-list")
    if phones_list:
        phones_list = phones_list.find_all("span", class_="js-phone")
        institution_data["phone_numbers"] = list(map(lambda phone: get_number(phone.find("a").get("href")), phones_list))

    site_link = soup.find(string=re.compile("омпания в сети"))
    if site_link:
        site_link = site_link.find_parent(class_="fluid")
        institution_data["social_networks"].append(site_link.find("a").get("href"))
        network_links = list(map(lambda link: link.find("a").get("href"), site_link.find_next_siblings(class_="fluid")))
        institution_data["social_networks"].extend(network_links)

    return institution_data


def parse_to_json(json_file, driver=None):
    institutions_info = []
    if not driver:
        driver = create_driver()

    soup = get_whole_page(test_url, driver)

    urls = get_all_institutions(soup)

    for number, url in enumerate(urls):
        try:
            institution_data = get_institution_data(url.strip())
            print(f"{number}) Link: {url.strip()} is done")
            institutions_info.append(institution_data)
        except Exception as ex:
            print(f"ERROR: Link {url} is broken")
            print(ex)

    with open(json_file, "w") as json_file:
        json.dump(institutions_info, json_file, indent=4, ensure_ascii=False)


def parser():
    driver = create_driver()
    list_of_cities = get_cities(site_home_url, driver)

    def choose(dict, alias):
        print(f"The list of {alias[:-1]}ies, where you can to get data from:")
        for name in dict.keys():
            print(name)
        while True:
            item = input(f'Choose the {alias} where you want to get data -> ')
            if item in dict.keys():
                break
            else:
                print("You entered an incorrect name. Try again.")
        return item

    city = choose(list_of_cities, "city")
    list_of_categories = get_categories(list_of_cities[city], driver)

    category = choose(list_of_categories, "category")
    category_url = list_of_categories[category]

    parse_to_json(category_url)



