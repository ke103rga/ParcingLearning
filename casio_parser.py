import unicodedata
from bs4 import BeautifulSoup
import requests
import os
import re
import json


def get_html_file(file_name, url):
    q = requests.get(url)
    text = q.text

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(text)


def get_all_pages(file_name, domen, dirpath):
    with open(file_name, "r", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    pag_container = soup.find("div", class_="bx-pagination-container")

    page = pag_container.find("li", class_="bx-pag-prev").find_next("li")
    pages_links = []

    while True:
        if len(page["class"]) == 0:
            link = f"{domen}{page.find('a').get('href')}"
            pages_links.append(link)
        elif str(page["class"][0]) == "bx-pag-next":
            break
        page = page.find_next("li")

    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

    os.replace(f"D:\\PythonProg\\PycharmProjects\\ParcingLearning\\{file_name}", f"{dirpath}/{file_name}")

    for index, link in enumerate(pages_links):
        get_html_file(f"{dirpath}/page{index}.html", link)


def get_clock_data(url):
    q = requests.get(url)
    soup = BeautifulSoup(q.content, "lxml")

    clock_data = {"name": "", "url": url,  "price": 0}

    brand = soup.find("h1", class_="product-card__title font-impact").text.strip()
    brand = brand[brand.find("Casio"):].strip().split()

    description = soup.find("h2", string="Описание").find_next("div", class_="accordion__body")\
        .find("p").get_text(strip=True)
    price = find_price(description)

    clock_data["name"] = f"{brand[0]} {brand[1]}, {brand[2]}"
    clock_data["price"] = price

    return clock_data


def find_price(description):
    pattern = r'(?<=от).*?(?=рублей)'
    price = re.findall(pattern, description)
    if len(price) != 0:
        price = unicodedata.normalize("NFKD", price[0])
        price = int("".join(price.split()))
    else:
        price = "TOFIND"
    return price


def parse_page(file_name, domen="https://shop.casio.ru"):
    with open(file_name, "r", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    links = list(map(lambda link: f"{domen}{link.get('href')}", soup.find_all("a", class_="product-item__link")))
    clocks = []
    count = 1

    for link in links:
        clocks.append(get_clock_data(link))
        print(f"{count}) Link: {link} is done.")
        count +=1

    return clocks


def casio_parser(dir_path, json_file):
    clocks_data = []

    for file in os.listdir(dir_path):
        clocks_data.extend(parse_page(f"{dir_path}/{file}"))

    with open(json_file, "w") as file:
        json.dump(clocks_data, file, indent=4, ensure_ascii=False)


#casio_parser("D:\PythonProg\PycharmProjects\ParcingLearning\clocks_data", "clocks.json")