import requests
import json
from setup.db import get_db_data, update_cell
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import logging
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()

XBLToken = os.getenv("XBLToken")
XBL_HEADERS  ={"X-BLToken": XBLToken}

SCRAPING_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,es;q=0.7,ro;q=0.6',
            'Referer': 'https://google.ro/',
            'DNT': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
    }



def get_link_from_sku(sku: str) -> str:
    logging.info("Getting link for sku")
    data = get_db_data()

    for row in data:
        if row["sku"] == sku:
            logging.info(f"Found link for sku: {sku}; {row['link']}")
            return row["link"]
        
    logging.error(f"Unable to find link for sku: {sku}")
    raise HTTPException(404, f"Unable to find link for sku: {sku}")



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
            headers=XBL_HEADERS,  
            timeout=14)
        
    except requests.Timeout:
        logging.error("BaseLinker POST request timed out")
        raise HTTPException(504, "Upstream server took too long to respond")
    
    except requests.RequestException as e:

        logging.error(f"Something when wrong with the post call to Base.\n{e}")
        raise HTTPException(502, f"Failed to update BaseLinker. {e}")
    
    return response


def get_imgs_from_link(url):        
    session = requests.Session()
    session.headers.update(SCRAPING_HEADERS)
    links = []
    formated_links={}

    try:
        response = session.get(url,  timeout=14)
        logging.info(f"Headers: {SCRAPING_HEADERS}")

    except requests.Timeout:
        logging.error("Emag GET request timed out")
        raise HTTPException(504, "Upstream server took too long to respond")
    
    except requests.RequestException as e:
        logging.error(f"Something went wrong with the requesto to {url}:\n{e}")
        raise HTTPException(status_code=502,
            detail=f"Something went wrong with the requesto to {url}:\n{e}")


    if response.status_code == 200:
        logging.info(f"Request made, Status code 200")

        soup = BeautifulSoup(response.text, 'html.parser')

        wraper = soup.find("div", class_="multimedia-gallery")
        if not wraper:
            raise HTTPException(502, "multimedia-gallery div not found")

        imgs = wraper.find_all("div", class_="thumbnail-wrapper")
        if not imgs:
            raise HTTPException(502, "No thumbnail-wrapper elements found")

        for img in imgs:
            a_tag = img.find("a")
            
            if a_tag and "href" in a_tag.attrs:
                link = a_tag["href"]
                links.append(link)

    else:
        logging.error(f"Something went wrong with the requesto to {url}.\nStatus code {response.status_code}. Error mesage: {response.text}")
        raise HTTPException(status_code=502,
            detail=f"Something went wrong with the requesto to {url}.\nStatus code {response.status_code}. Error mesage: {response.text}")

    if len(links) >= 1:    
        logging.info(f"Found a total of {len(links)} images: {links}")
        for index, imgs_link in enumerate(links):
            formated_links[index] = f"url:{imgs_link}"    
        return formated_links
    else:
        logging.error(f"Found images are less than 1. {links}")
        raise HTTPException(status_code=502,
            detail=f"Found images are less than 1. {links}")

