import requests
import json
from setup.db import get_db_data, update_cell
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()

XBLToken = os.getenv("XBLToken")
headers ={"X-BLToken": XBLToken}



def get_link_from_id(item_id: str) -> str:
    data = get_db_data()

    for row in data:
        if row["item_id"] == item_id:
            return row["link"]
    return None



def update_images_base(invetory_id: str, product_id: str, photos: dict):
    payload = {
            "method":"addInventoryProduct",
            "parameters":json.dumps({
                "inventory_id": invetory_id,
                "product_id": product_id,
                "images": photos
        })}
    response = requests.post(
        "https://api.baselinker.com/connector.php", 
        data=payload,
        headers=headers)

    print(response.status_code)
    print(response.text)


def get_imgs_from_link(url):
    links = []
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    name = soup.find("h1", class_="page-title").text.strip().replace("/", "{")

    wraper = soup.find("div", class_="multimedia-gallery")
    imgs = wraper.find_all("div", class_="thumbnail-wrapper")

    for img in imgs:
        a_tag = img.find("a")
        
        if a_tag and "href" in a_tag.attrs:
            link = a_tag["href"]
            links.append(link)
    return links


