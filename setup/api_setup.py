import requests
import json
from setup.db import get_db_data, update_cell
from dotenv import load_dotenv
import os

load_dotenv()

XBLToken = os.getenv("XBLToken")
headers ={"X-BLToken": XBLToken}



def grab_inventories() -> list:
    payload = {
        "method": "getInventories",
    }
    response = requests.post(
        "https://api.baselinker.com/connector.php",
        data=payload,
        headers=headers
    )
    
    return [invetory["inventory_id"] for invetory in response.json()["inventories"]]


def grab_items_for_inv(inv_id: str) -> list:
    payload = {
        "method": "getInventoryProductsList",
        "parameters": json.dumps({
            "inventory_id": inv_id
        }

        )}
    
    response = requests.post(
        "https://api.baselinker.com/connector.php",
        data=payload,
        headers=headers
    )


    """
    keys = response.json()["products"].keys()
    items_data = [{key:response.json()["products"][key]} for key in keys]
    """


    values = list(response.json()["products"].values())
    return values


def write_id():
    total_count=0
    writes_count = 0
    api_data = grab_items_for_inv(86148)

    sheet_data = get_db_data()

    for row in sheet_data[:10]:
        total_count+=1
        item_data = [item for item in api_data if item["sku"] == row["sku"]]

        if item_data:
            item_id = item_data[0]["id"]
            update_cell(row=row["_sheet_row"],column=4,text=item_id)
            writes_count+=1

        else:
            print(f"nu am gasit -- {row["sku"]}")


    print("total: ", total_count)
    print("writes: ", writes_count)

write_id()
