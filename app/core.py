import json
from setup.db import get_db_data, update_cell, sheet
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import logging
from fastapi import HTTPException
import time
import random
import curl_cffi.requests as requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def log_session_debug(session, response=None):
    logging.info("=== SESSION HEADERS ===")
    for k, v in session.headers.items():
        logging.info(f"{k}: {v}")

    logging.info("=== SESSION COOKIES ===")
    logging.info(session.cookies)
        
    if response is not None:
        logging.info("=== REQUEST HEADERS SENT ===")
        for k, v in response.request.headers.items():
            logging.info(f"{k}: {v}")

    logging.info("=========================")

load_dotenv()

XBLToken = os.getenv("XBLToken")
XBL_HEADERS  ={"X-BLToken": XBLToken}

SCRAPING_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,es;q=0.7,ro;q=0.6',
            'Referer': 'https://google.ro/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Chromium";v="118", "Not=A?Brand";v="24", "Google Chrome";v="118"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
    }



def get_link_from_sku(sku: str) -> str:
    logging.info("Getting link for sku")
    data = get_db_data()

    for row in data:
        if row["sku"] == sku:
            logging.info(f"Found link for sku: {sku}; {row['link']}")
            return row["link"]
        
    logging.info(f"Unable to find link for sku: {sku}")
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
            headers=XBL_HEADERS
           )
        
    except requests.Timeout:
        logging.error("BaseLinker POST request timed out")
        raise HTTPException(504, "Upstream server took too long to respond")
    
    except requests.RequestException as e:

        logging.error(f"Something when wrong with the post call to Base.\n{e}")
        raise HTTPException(502, f"Failed to update BaseLinker. {e}")
    
    return response


def get_imgs_from_link(url:str, session: requests.Session):        
    links = []
    formated_links={}

    try:
        response = session.get(url,  timeout=14)
        

    except requests.Timeout:
        logging.error("Emag GET request timed out")
        raise HTTPException(504, "Upstream server took too long to respond")
    
    except requests.RequestException as e:
        logging.error(f"Something went wrong with the requesto to {url}:\n{e}")
        raise HTTPException(status_code=502,
            detail=f"Something went wrong with the requesto to {url}:\n{e}")

    log_session_debug(session=session, response=response)

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

 


#### SCRAPING NEW ITEMS ####


def get_dbs_sku() -> list:
    
    sheet_data = get_db_data()
    sheets_sku = [row["sku"] for row in sheet_data if row["sku"] != ""]
    return sheets_sku

def get_dbs_links() -> list:
    
    sheet_data = get_db_data()
    sheets_links = [row["link"] for row in sheet_data if row["link"] != ""]
    return sheets_links

def grab_sku(url, session: requests.session):
    try:
        response = session.get(url)
        log_session_debug(session=session, response=response)

        soup = BeautifulSoup(response.text, 'html.parser')
        sku = soup.find("div", class_="main-container-inner").find("main", class_="main-container").find("section", class_="page-section").find("div", class_="container").find("div", class_="justify-content-between").find("span", class_="product-code-display").text
        return sku.replace("                    Cod produs: ", "").strip()
    except:
        return None
    

def grab_links(session: requests.Session):
    sheets_sku = get_dbs_sku()
    sheets_links = get_dbs_links()
    print(f"SKU in sheet: {len(sheets_sku)}")

    for i in range(1,2):
        bulk_items = []

        url = f"https://www.emag.ro/brands/brand/nextly/sort-offer_iddesc/p{i}"
        try:
            response = session.get(url)
        except Exception as e:
            logging.exception("Request failed for %s", url)
            raise HTTPException(status_code=502, detail=f"Request failed for {url}")
        if response.status_code != 200:
            logging.error(f"Request failed for {url}\n. Status code: {response.status_code}, text: {response.text}")
            raise HTTPException(status_code=502,
            detail=f"Something went wrong with the requesto to {url}.\nStatus code {response.status_code}. Error mesage: {response.text}")
        
        log_session_debug(session=session, response=response)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        container = soup.find("div", class_="js-products-container")

        if not container:
            logging.error("Products container not found on %s", url)
            raise HTTPException(status_code=502,
            detail=f"Products container not found on {url}")

        items = container.find_all("div", class_="card-item")
        for item in items:
            bulk_items.append({
                "item_name": item.get("data-name"),
                "link": item.get("data-url"),
            })

        logging.info(f"Bulk items scraped: {len(bulk_items)}", )


        new_bulk_items = [item for item in bulk_items if item["link"] not in sheets_links]

        logging.info(f"New bulk items after cleanup: {len(new_bulk_items)}")

        time.sleep(3)
        
        for item in new_bulk_items:
            sku = grab_sku(item["link"], session=session)

            if sku:
                item["sku"] = sku
            else:
                item["sku"] = None

            time.sleep(random.randint(2,6))

        count=0    
        for item in new_bulk_items:
        
            if item["sku"] not in sheets_sku and item["sku"] != None:
                sheet.append_row([item["item_name"], item["link"], item["sku"]])
                count+=1
        logging.info(f"Total writes from on bulk: {count}")

