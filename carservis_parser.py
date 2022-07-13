from bs4 import BeautifulSoup
import requests
import os


def get_html_first_page(file_name, url):
    q = requests.get(url)
    text = q.text

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(text)


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
    print(amount_of_pages)

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    for i in range(2, amount_of_pages + 1):
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


def get_wheel_data(link):
    # q = requests.get(link)
    # soup = BeautifulSoup(q.content, "lxml")

    with open(link, "r") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    wheel_data = {"name": "", "url": link, "image_url": "", "single_price": 0, "group_price": 0}

    info = soup.find("div", class_="card-product__body")

    wheel_data["name"] = info.find("h1", class_="title-small").text.strip()
    wheel_data["image_url"] = info.find("div", class_="card-product__img").find("img").get("src")

    prices = info.find("div", class_="card-product__prices")

    single_price = prices.find(class_="card-product__price card-product__price_single").\
        find("span").text.split()[:-1]
    wheel_data["single_price"] = int("".join(single_price))

    group_price = prices.find(class_="card-product__price card-product__price_multiple").text.split()
    wheel_data["group_price"] = int("".join(group_price[:group_price.index("₽")]))
