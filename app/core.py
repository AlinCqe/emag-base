import requests
import json
from setup.db import get_db_data, update_cell
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()

XBLToken = os.getenv("XBLToken")
headers ={"X-BLToken": XBLToken}



def get_link_from_sku(sku: str) -> str:
    logging.info("Getting link for sku")
    data = get_db_data()

    for row in data:
        if row["sku"] == sku:
            logging.info(f"Found link for sku: {sku}; {row["link"]}")
            return row["link"]
    logging.error(f"Unable to find link for sku: {sku}")
    return None



def update_images_base(inventory_id: str, item_id: str, images: dict):
    
    payload = {
            "method":"addInventoryProduct",
            "parameters":json.dumps({
                "inventory_id": inventory_id,
                "product_id": item_id,
                "images": images
        })}
    logging.info(f"Sending api request to Base with payload: \n{payload}")

    try:
        
        response = requests.post(
            "https://api.baselinker.com/connector.php", 
            data=payload,
            headers=headers)
        
    except Exception as e:
        logging.error(f"Something when wrong with the post call to Base.\n{e}")

    return [response]



def get_imgs_from_link(url):        
    links = []
    formated_links={}

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        logging.error(f"Something went wrong with the requesto to {url}:\n{e}")
        return None
    
    if response.status_code == 200:
        logging.info(f"Request made, Status code 200")

        soup = BeautifulSoup(response.text, 'html.parser')

        wraper = soup.find("div", class_="multimedia-gallery")
        imgs = wraper.find_all("div", class_="thumbnail-wrapper")

        for img in imgs:
            a_tag = img.find("a")
            
            if a_tag and "href" in a_tag.attrs:
                link = a_tag["href"]
                links.append(link)
    else:
        logging.error(f"Something went wrong with the requesto to {url}.\nStatus code {response.status_code}. Error mesage: {response.text}")

    if len(links) >= 1:    
        logging.info(f"Found a total of {len(links)} images: {links}")
        for index, imgs_link in enumerate(links):
            formated_links[index] = f"url:{imgs_link}"    
        return formated_links
    else:
        logging.error(f"Found images are less than 1. {links}")
        return None


