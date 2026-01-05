from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from .core import get_imgs_from_link, update_images_base, get_link_from_sku
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

class ItemRequest(BaseModel):
    id: int
    inventory_id: int


@app.head("/UpdateImages")
def update_images():
    return Response(status_code=200)


@app.get("/UpdateImages")
def update_images(id:str, sku:str, inventory_id:str):
    logger.info(f"Received item: {sku}")
    link = get_link_from_sku(sku)

    logger.info(f"Link: {link}")
    imgs = get_imgs_from_link(link)

    if not imgs:
       raise HTTPException(
            status_code=404,
            detail=f"No images found for item sku {sku}, link: {link}"
        )
    
    logger.info(f"Images: {imgs}")
    response = update_images_base(inventory_id=inventory_id, item_id=id, images=imgs)
    if response.status_code == 200:
        return {"status": "ok"}
    