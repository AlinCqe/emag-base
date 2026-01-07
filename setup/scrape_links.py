import requests
import random
from bs4 import BeautifulSoup
import time
from .db import get_db_data, update_cell, sheet
signs = [':', '*', '?', '"', '<', '>', '|']

    

data = get_db_data()


headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,es;q=0.7,ro;q=0.6',
            'Referer': 'https://google.ro/',
            'DNT': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
    }



def grab_sku(url):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        sku = soup.find("div", class_="main-container-inner").find("main", class_="main-container").find("section", class_="page-section").find("div", class_="container").find("div", class_="justify-content-between").find("span", class_="product-code-display").text
        return sku.replace("                    Cod produs: ", "").strip()
    except:
        return None
    

def write_sku():
    data = [row for row in data if row["status"] == ""]

    for item in data:

        sku = grab_sku(item["link"])
        print(sku)

        update_cell(row=item["_sheet_row"], column=3, text=sku)
        time.sleep(random.randint(1,2))

def bulk_grab_links():
    n=0
    total=0
    for i in range(1,25):
        link = f"https://www.emag.ro/brands/brand/nextly/sort-offer_iddesc/p{i}"
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sku = soup.find("div", class_="main-container-inner").find("main", class_="main-container").find("section", class_="page-section").find("div", class_="container").find("div", class_="justify-content-between").find("span", class_="product-code-display")
            print(sku)
            items = soup.find("div", class_="js-products-container").find_all("div", class_="card-item")
            for item in items:

                total+=1
                n+=1    
                #sheet.append_row([item["data-name"], item["data-url"]])
                time.sleep(2)

            print(f"url: {link}, total= {n}")
            time.sleep(5)
        else:
            print("Bad status code", response.status_code)
            time.sleep(5)
    print(f"total= {total}")


def get_dbs_sku() -> list:
    
    sheet_data = get_db_data()
    sheets_sku = [row["sku"] for row in sheet_data if row["sku"] != ""]


    return sheets_sku


def get_dbs_links() -> list:
    
    sheet_data = get_db_data()
    sheets_links = [row["link"] for row in sheet_data if row["link"] != ""]


    return sheets_links


    
def daily_grab_links():
    sheets_sku = get_dbs_sku()
    sheets_links = get_dbs_links()
    print(f"SKU in sheet: {len(sheets_sku)}")

    for i in range(1,3):
        bulk_items = []

        link = f"https://www.emag.ro/brands/brand/nextly/sort-offer_iddesc/p{i}"
        try:
            response = requests.get(link, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.find("div", class_="js-products-container").find_all("div", class_="card-item")
            for item in items:
                bulk_items.append({"item_name":item["data-name"], "link":item["data-url"]})

        else:
            print("Bad status code", response.status_code)
        
        print(f"Bulk items: {len(bulk_items)}")

        new_bulk_items = [item for item in bulk_items if item["link"] not in sheets_links]

        print(f"Bulk items after links clean up: {len(new_bulk_items)}.\n{new_bulk_items}")

        time.sleep(10)
        for item in new_bulk_items:
            sku = grab_sku(item["link"])

            if sku:
                item["sku"] = sku

            time.sleep(random.randint(3,6))

        count=0    
        for item in new_bulk_items:
        
            if item["sku"] not in sheets_sku and item["sku"] != None:
                sheet.append_row([item["item_name"], item["link"], item["sku"]])
                count+=1
        print(f"Total writes from one bulk: {count}")




daily_grab_links()