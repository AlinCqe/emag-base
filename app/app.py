from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from app.core import get_imgs_from_link, update_images_base, get_link_from_sku, grab_links, SCRAPING_HEADERS
import logging
import threading
import curl_cffi.requests as requests

update_images_lock = threading.Lock()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_session_lock = threading.Lock()
_shared_session: requests.Session | None = None

def get_shared_session() -> requests.Session:
    global _shared_session

    with _session_lock:
        if _shared_session is None:
            session = requests.Session()
            session.headers.update(SCRAPING_HEADERS)
            _shared_session = session

        return _shared_session
    

app = FastAPI()




@app.head("/UpdateImages")
@app.get("/UpdateImages")
def update_images(id:str, sku:str, inventory_id:str):
    with update_images_lock:
        logger.info(f"Received item: {sku}")

        session = get_shared_session() 

        link = get_link_from_sku(sku)
        if not link:
            logger.info(f"Starting to scrape links")
            grab_links(session) 


        link = get_link_from_sku(sku)
        if not link:
            logger.error(f"No link found for sku: {sku}")
            raise HTTPException(
                status_code=404,
                detail=f"No link found for sku: {sku}"
            )
            

        logger.info(f"Link: {link}")
        imgs = get_imgs_from_link(link, session)
        
        if not imgs:
            raise HTTPException(
                status_code=404,
                detail=f"No images found for item sku {sku}, link: {link}"
            )

        response = update_images_base(inventory_id=inventory_id, item_id=id, images=imgs)

        logger.info(
            f"Base api call status code: {response.status_code}.\nFull message: {response.text}"
        )

        if response.status_code != 200:
            logger.error(f"HTTP error from BaseLinker: {response.status_code}")
            raise HTTPException(
                status_code=502,
                detail="BaseLinker HTTP error"
            )

        data = response.json()

        if data.get("status") != "SUCCESS":
            logger.warning(f"BaseLinker API error: {data}")
            raise HTTPException(
                status_code=400,
                detail=f"{data.get('error_code')} - {data.get('error_message')}"
            )

        return {"status": "ok"}