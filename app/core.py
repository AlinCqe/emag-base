import requests
import json
from setup.db import get_db_data, update_cell
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()

XBLToken = os.getenv("XBLToken")
headers ={"X-BLToken": XBLToken}



def get_link_from_sku(sku: str) -> str:
    data = get_db_data()

    for row in data:
        print(row)
        if row["sku"] == sku:
            return row["link"]
    return None



def update_images_base(invetory_id: str, item_id: str, images: dict):
    payload = {
            "method":"addInventoryProduct",
            "parameters":json.dumps({
                "inventory_id": invetory_id,
                "product_id": item_id,
                "images": images
        })}
    response = requests.post(
        "https://api.baselinker.com/connector.php", 
        data=payload,
        headers=headers)

    return [response]



def get_imgs_from_link(url):        #safe out if no photos, make this robust
    links = []
    formated_links={}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')


        wraper = soup.find("div", class_="multimedia-gallery")
        imgs = wraper.find_all("div", class_="thumbnail-wrapper")

        for img in imgs:
            a_tag = img.find("a")
            
            if a_tag and "href" in a_tag.attrs:
                link = a_tag["href"]
                links.append(link)

    
    if len(links) >= 1:    
        for index, imgs_link in enumerate(links):
            formated_links[index] = f"url:{imgs_link}"    
        return formated_links
    
    return None


