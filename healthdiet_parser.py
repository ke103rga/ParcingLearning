from bs4 import BeautifulSoup
import requests
import json


def get_categories_list():
    url = "http://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

    q = requests.get(url)
    content = q.text

    with open("healh_diet.html", "w") as file:
        file.write(content)

    with open("healh_diet.html", "r") as file:
        src = file.read()

        soup = BeautifulSoup(src, "lxml")

        categories = soup.find_all('a', class_="mzr-tc-group-item-href")
        categories_links = [category.get("href") for category in categories]

    with open("categories.txt", "w") as file:
        for link in categories_links:
            file.write(f"http://health-diet.ru{link}\n")


def parse_to_json(file_name):
    with open("categories.txt", "r") as file:
        meals_data = []
        count = 1
        for link in file:
            q = requests.get(link.strip())
            soup = BeautifulSoup(q.content, "lxml")

            table = soup.find("tbody")

            meals = table.find_all("tr")
            for meal in meals:
                meal_data = {"name": "", "caloric": 0, "proteins": 0, "fats": 0, "carbohydrates": 0}

                parameters = meal.find_all("td")

                meal_data["name"] = parameters[0].text.strip()

                meal_data["caloric"] = parameters[1].text

                meal_data["proteins"] = parameters[2].text

                meal_data["fats"] = parameters[3].text

                meal_data["carbohydrates"] = parameters[4].text

                meals_data.append(meal_data)
            print(f"{count}) Category: {link} is done")
            count += 1

    with open(file_name, "w") as json_file:
        json.dump(meals_data, json_file, indent=4)

    return meals_data


def get_html_page(file_name, url):
    with open(file_name, "w") as file:
        q = requests.get(url)
        text = q.text

        file.write(text)


def attempt(file_name):
    with open(file_name, "r") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    meals_data = []

    table = soup.find("tbody")

    meals = table.find_all("tr")
    for meal in meals:
        meal_data = {"name": "", "caloric": 0,
                     "proteins": 0, "fats": 0, "carbohydrates": 0}

        parameters = meal.find_all("td")

        meal_data["name"] = parameters[0].text.strip()

        meal_data["caloric"] = parameters[1].text

        meal_data["proteins"] = parameters[2].text

        meal_data["fats"] = parameters[3].text

        meal_data["carbohydrates"] = parameters[4].text

        meals_data.append(meal_data)
        print(meal_data)

    print(meals_data)


def create_name(title):
    if title.startswith("РҐРёРјРёС‡РµСЃРєРёР№ СЃРѕСЃС‚Р°РІ РїСЂРѕРґСѓРєС‚Р°: "):
        return title.split(":")[1].strip()


#parse_to_json("diet_table.json")

