import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = "service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("links").sheet1

def get_db_data():


    raw_data = sheet.get_all_records()

    data = []
    for i, row in enumerate(raw_data, start=2):  
        row_dict = dict(row)
        
        row_dict["_sheet_row"] = i
        data.append(row_dict)

    return data

def update_cell(row: int, column: int, text:str):

    sheet.update_cell(row, column, text)

def col_index():
    data=sheet.get_all_records()
    headers = list(data[0].keys()) 
    col_index = {name: idx + 1 for idx, name in enumerate(headers)}
