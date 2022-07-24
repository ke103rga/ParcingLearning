from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import requests
import re
import time


driver = webdriver.Chrome("C:\\Users\\Виктория\\PycharmProjects\\UniversitiesParser\\chromedriver_win32\\chromedriver.exe")
test_url = "https://omsk.zoon.ru/beauty/"


def get_whole_page(driver, url, download_file=None):
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


def parse_to_json(json_file):
    institutions_info = []

    soup = get_whole_page(driver, test_url)

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


#parse_to_json("omsk_beauty_institutions.json")

