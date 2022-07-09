from bs4 import BeautifulSoup
import requests
import json


def get_html_file(file_name, url):
    q = requests.get(url)
    text = q.text

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(text)


fest_categories = {"mainstream": {"ajax_url": "https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=8%20Jul%202022&to_date=&genre%5B%5D=pop&maxprice=500&o=24&bannertitle=August", "offset": 24},
                   "boutique": {"ajax_url": "https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=9%20Jul%202022&to_date=&maxprice=500&o=24&bannertitle=June", "offset": 168},
                   "family_friendly": {"ajax_url": "https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=9%20Jul%202022&to_date=&maxprice=500&o=24&bannertitle=August", "offset": 168},
                   "rock_metal": {"ajax_url": "https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=9%20Jul%202022&to_date=&genre%5B%5D=rock&maxprice=500&o=24&bannertitle=September", "offset": 24},
                   "dance": {"ajax_url": "https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=9%20Jul%202022&to_date=&genre%5B%5D=house&genre%5B%5D=trance&genre%5B%5D=hard%20dance&genre%5B%5D=electronic&genre%5B%5D=edm&maxprice=500&o=24&bannertitle=August", "offset": 72},
                   "budget": {"ajax_url": "https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&from_date=9%20Jul%202022&to_date=&maxprice=100&o=24&bannertitle=July", "offset": 144}}

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36 OPR/88.0.4412.74 (Edition Yx 02)"
}

fests_data = []


def get_fest_category(category, ajax_url, offset):
    for i in range(0, offset, 24):
        start_index = ajax_url.find("o=")
        end_index = ajax_url.find("&", start_index)
        ajax_url = ajax_url[:start_index + 2] + str(i) + ajax_url[end_index:]

        q = requests.get(url=ajax_url, headers=headers)
        json_data = json.loads(q.text)
        html_response = json_data["html"]

        with open(f"fest_data/{category}{i%24}.html", "a", encoding="utf-8") as file:
            file.write(html_response)


def count_links(filename):
    with open(filename, "r") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    links = soup.find_all("h3", class_="card-title")

    print(len(links))


def get_fest_categories():
    for category in fest_categories:
        get_fest_category(category, **fest_categories.get(category))


def check(filename):
    with open(filename, "r") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    titles = soup.find_all("h3", class_="card-title")
    links = list(map(lambda title: f'https://www.skiddle.com{title.find("a").get("href")}', titles))

    for link in links:
        fest_info = {"name": "", "date": "", "contacts": {}}

        q = requests.get(url=link, headers=headers)
        soup = BeautifulSoup(q.content, "lxml")

        name = soup.find("h1", class_="tc-white").text
        date = soup.find("h3", class_="tc-white").text
        fest_info["name"] = name
        fest_info["date"] = date
        contacts_link = soup.find("span", class_="icon-newmap margin-right-5").find_next("a").get("hef")

        q = requests.get(url=f"https://www.skiddle.com{contacts_link}", headers=headers)
        soup = BeautifulSoup(q.content, "lxml")

        contacts = soup.find("h2", string="Venue contact details and info").find_next("div").find_all("p")
        for contact in contacts:
            contact = contact.text.strip().split(": ")
            fest_info["contacts"][contact[0]] = contact[1]

        fests_data.append(fest_info)


def parser(file_name):
    files = list(map(lambda category: f"fest_data/{category}0.html", fest_categories.keys()))

    for file in files:
        check(file)

    with open(file_name, "w") as json_file:
        json.dump(fests_data, json_file, indent=4)




