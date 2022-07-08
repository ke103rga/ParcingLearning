import requests
from bs4 import BeautifulSoup
import json

# members_urls = []
# self_members_urls = []
#
# for i in range(1, 737, 20):
#     url = f"https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=20&noFilterSet=true&offset={i}"
#
#     q = requests.get(url)
#     q = q.content
#
#     soup = BeautifulSoup(q, "lxml")
#
#     members = [div.find("a").get("href") for div in soup.find_all(name="div", class_="bt-slide-content")]
#     self_members_urls.extend(members)
#
#     persons = soup.find_all(class_="bt-open-in-overlay")
#     for person in persons:
#         person_page_url = person.get("href")
#         members_urls.append(person_page_url)
#
# with open("members_list.txt", "a") as file:
#     for url in members_urls:
#         file.write(f"{url}\n")
#
# with open("people_list.txt", "a") as file:
#     for url in self_members_urls:
#         file.write(f"{url}\n")


with open("members_list.txt", "r") as file:
    count = 1

    members = [line.strip() for line in file.readlines()]
    members_data = []
    member_data = {"name": "", "party": "", "links": {}}

    for line in members:
        q = requests.get(line)
        result = q.content

        soup = BeautifulSoup(result, "lxml")

        biography_row = soup.find(name="div", class_="bt-biografie-name").find("h3").text.strip().split(",")
        member_data["name"] = biography_row[0]
        member_data["party"] = biography_row[1]

        #internet_profile = soup.find(string="Profile im Internet").find_next(class_="bt-linkliste")
        links = soup.find_all("a", class_="bt-link-extern")
        member_data["links"] = {link.get("title"): link.get("href") for link in links}

        members_data.append(member_data)
        print(f"{count}: URL: {line} is done")
        count += 1

with open("members.json", "w") as json_file:
    json.dump(members_data, json_file, indent=4)


