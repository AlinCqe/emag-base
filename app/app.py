from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .core import get_imgs_from_link, update_images_base, get_link_from_id
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

class ItemRequest(BaseModel):
    id: int
    inventory_id: int


@app.post("/UpdateImages")
def update_images(item: ItemRequest):
    logger.info(f"Received item: {item}")
    print(item.id)
    link = get_link_from_id(item.id)
    print(link)
    if not link:
        raise HTTPException(
            status_code=404,
            detail=f"No link found for item id {item.id}"
        )
    
    logger.info(f"Link: {link}")
    imgs = get_imgs_from_link(link)

    if not imgs:
       raise HTTPException(
            status_code=404,
            detail=f"No images found for item id {item.id}, link: {link}"
        )
    
    logger.info(f"Images: {imgs}")
    response = update_images_base(invetory_id=1, item_id=item.id, images=imgs)
    return {"status": "ok"}