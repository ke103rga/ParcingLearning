from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import json
import time
from tqdm import tqdm


driver = webdriver.Chrome("D:\PythonProg\PycharmProjects\ParcingLearning\chrome_driver\chromedriver.exe")


def get_html_first_page(file_name, url):
    q = requests.get(url)
    text = q.text

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(text)


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


def get_links(soup, domen="https://roscarservis.ru"):
    items = soup.find("div", class_="catalog__items-container").find_all("div", class_="catalog__item")
    urls = list(map(lambda url: url.find("a", class_="catalog-item__img"), items))
    links = list(map(lambda link: f'{domen}{link.get("href")}', urls[:12]))
    return links


def get_all_links(file_name, dir_path="D:\PythonProg\PycharmProjects\ParcingLearning\wheels_data"):
    with open(file_name, "r", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    links = get_links(soup)

    amount_of_pages = int(soup.find("a", class_="pagination__arrow pagination__arrow_right").\
        find_previous("a", class_="pagination__page").text)

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    for i in tqdm(range(2, amount_of_pages + 1)):
        url = f"https://roscarservis.ru/catalog/legkovye/?sort%5Bprice%5D=asc&form_id=catalog_filter_form&filter_mode" \
              f"=params&filter_type=tires&arCatalogFilter_415=&arCatalogFilter_416=&raznFilter%5Brear%5D%5B415%5D" \
              f"=&raznFilter%5Brear%5D%5B416%5D=&arCatalogFilter_417=&arCatalogFilter_431=&arCatalogFilter_433" \
              f"=&arCatalogFilter_440=&arCatalogFilter_430=&arCatalogFilter_432=&arCatalogFilter_434" \
              f"=&arCatalogFilter_438=&arCatalogFilter_439=&car_brand=&car_model=&car_year=&car_mod=&diskType=1" \
              f"&set_filter=Y&isAjax=true&PAGEN_1={i} "

        q = requests.get(url)
        soup = BeautifulSoup(q.content, "lxml")
        links.extend(get_links(soup))

    with open(f"{dir_path}/wheels_links.txt", "w", encoding="utf-8") as file:
        for link in links:
            print(link.strip(), file=file)


def get_amount(soup):

    def make_digit(count):
        for symbol in count:
            if not symbol.isdigit():
                count = count.replace(symbol, "")

        return int(count)

    tabs = soup.find("div", class_="tabs-link__tabs").find("div", class_="table-count").\
        find_all("div", class_="table-count__row")

    rows = list(map(lambda tab: tab.find("div", class_="table-count__cell").find_next("div", class_="table-count__cell"), tabs))
    counts = list(map(lambda row: row.find(class_="table-count__text").text.strip(), rows))

    is_more = any([count.strip().startswith(">") for count in counts])

    amount = sum(list(map(lambda count: make_digit(count), counts)))

    if is_more:
        return f">{amount}"
    else:
        return str(amount)


def get_wheel_data(link, image_domen="https://roscarservis.ru"):
    try:
        driver.get(link)
        time.sleep(5)
        src = driver.page_source
    except Exception:
        print(f"Page {link} is not found")

    # with open(link, "r", encoding="utf-8") as file:
    #     src = file.read()

    soup = BeautifulSoup(src, "lxml")
    wheel_data = {"name": "", "url": link, "image_url": "", "single_price": 0, "group_price": 0, "amount": ""}

    info = soup.find("div", class_="card-product__body")

    wheel_data["name"] = info.find("h1", class_="title-small").text.strip()
    wheel_data["image_url"] = f'{image_domen}{info.find("div", class_="card-product__img").find("img").get("src")}'

    prices = info.find("div", class_="card-product__prices")

    single_price = prices.find(class_="card-product__price card-product__price_single").\
        find("span").text.split()[:-1]
    wheel_data["single_price"] = ("".join(single_price))

    group_price = prices.find(class_="card-product__price card-product__price_multiple").text.split()
    wheel_data["group_price"] = ("".join(group_price[:group_price.index("₽")]))
    wheel_data["amount"] = get_amount(soup)

    return wheel_data


def parser(filename, json_file):
    wheels_data = []

    with open(filename, "r") as file:
        links = list(map(lambda link: link.strip(), file.readlines()))
        for link in tqdm(links):
            wheels_data.append(get_wheel_data(link))

        driver.close()
        driver.quit()

    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(wheels_data, file, indent=4, ensure_ascii=False)


def main():
    dir_path = "D:\PythonProg\PycharmProjects\ParcingLearning\wheels_data"
    first_page_link = input("Enter the url of the first page in catalog -> ")
    first_page = get_page_with_selenium(first_page_link, f"{dir_path}\\first_page.html")

    need_update_links = input("Do you want to update links of the wheels?(y/n) -> ")
    if need_update_links == "y":
        change_dir_path = input("Do you want to change the directory with the file which contains links?(y/n) -> ")
        if change_dir_path == "y":
            dir_path = input("Enter the new path to directory -> ")
        print("It can takes a lot of time")
        print("[...   Loading links   ...]")
        get_all_links(first_page, dir_path)
        print("All links were saved successfully")

    json_file = input("Enter name of json file where result will ba saved -> ")
    print("Ok, we are ready to start")
    print("[...   Loading info   ...]")
    parser(f"{dir_path}/try", json_file)
    print(f"All data saved successfully. Just check the {json_file}")


parser("wheels_data/wheels_links.txt", "wheels.json")

