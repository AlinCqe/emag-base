from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .core import get_imgs_from_link, update_images_base, get_link_from_id
app = FastAPI()

class ItemRequest(BaseModel):
    id: int
    inventory_id: int


@app.post("/UpdateImages")
def update_images(item: ItemRequest):

    link = get_link_from_id(str(item.id))

    if not link:
        raise HTTPException(
            status_code=404,
            detail=f"No link found for item id {item.id}"
        )
    

    imgs = get_imgs_from_link(link)

    if not imgs:
        raise HTTPException(
            status_code=404,
            detail=f"No images found for item id {item.id}, link: {link}"
        )
    

    response = update_images_base(invetory_id=1, item_id=item.id, images=imgs)
    return response