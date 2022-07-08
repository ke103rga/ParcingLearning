from bs4 import BeautifulSoup
import re


with open("index.html", encoding="utf-8") as file:
    src = file.read()
#print(src)

soup = BeautifulSoup(src, "lxml")

title = soup.title
#print(title.text)
#print(title.string)

page_h1 = soup.find("h1")
#print(page_h1.text)

page_all_h1 = soup.find_all("h1")
#for h1 in page_all_h1:
#    print(h1.string)

user_name = soup.find(name="div", class_="user__name")
name = user_name.find("span")
#print(name.text)

user_name = soup.find(name="div", attrs={"class": "user__name"}).find("span").text
#print(user_name)

user_span = [item.find_all(name="span") for item in soup.find_all(name="div", class_="user__info")]
#for item in user_span:
#   for span in item:
#      print(span.text)

social_networks = soup.find(class_="social__networks").find_all(name="a")
for network in social_networks:
    start_index = str(network).find('\"')
    end_index = str(network).find('\"', start_index+1)
    #print(f"{network.text} - {str(network)[start_index+1:end_index]}")
    #print(f"{network.text} - {network.get('href')}")
    # Метод get достает текст из атрибута

head = soup.find("meta").find_parent()
#print(head)
ex = soup.find(string="Ссылки на соц.сети:").find_parents(limit=2)
#print(ex[0].name)

post_titles = soup.find_all(class_="post__title")
for post_title in post_titles:
    while "h" not in post_title.name:
        post_title = post_title.find_next()
    #print(post_title.text)

tag = soup.find(string="Ссылки на соц.сети:")
for i in range(4):
    tag = tag.find_next()
    #print(i, tag, end="\n\n")

inst_link = soup.find("a", string="Instagram")
#print(inst_link.find_previous_sibling())

user_city = soup.find("div", class_="user__city", )
user_city = user_city.find_next()
#print(user_city.text, end=" ")
#print(user_city.find_next_sibling().text)

doc_links = soup.find_all("a", string=re.compile("Insta"))
[print(link.get("href")) for link in doc_links]



