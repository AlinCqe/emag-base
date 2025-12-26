from fastapi import FastAPI
from pydantic import BaseModel
from .core import get_imgs_from_link, update_images_base, get_link_from_id
app = FastAPI()

class ItemRequest(BaseModel):
    id: int
    inventory_id: int


@app.post("/UpdateImages")
def update_images(item: ItemRequest):
    link = get_link_from_id(str(item.id))
    if link:
        images = get_imgs_from_link(link)
        return images