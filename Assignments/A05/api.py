"""item Store API

item Store API built with FastAPI.

"""

from fastapi import FastAPI, Query, Path, Body
from fastapi.responses import RedirectResponse, FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from store_database import StoreDatabase
from contextlib import asynccontextmanager
import uvicorn
import json
import os
from rich import print
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import requests
from models import Item, Category, User


# ██████   █████  ███████ ███████     ███    ███  ██████  ██████  ███████ ██      ███████
# ██   ██ ██   ██ ██      ██          ████  ████ ██    ██ ██   ██ ██      ██      ██
# ██████  ███████ ███████ █████       ██ ████ ██ ██    ██ ██   ██ █████   ██      ███████
# ██   ██ ██   ██      ██ ██          ██  ██  ██ ██    ██ ██   ██ ██      ██           ██
# ██████  ██   ██ ███████ ███████     ██      ██  ██████  ██████  ███████ ███████ ███████


TAGS_METADATA: list[dict[str, str]] = [
    {
        "name": "/",
        "description": "Redirects to the docs.",
    },
    {
        "name": "Items",
        "description": "Operations with items.",
    },
    {
        "name": "Categories",
        "description": "Operations with categories.",
    },
    {
        "name": "Images",
        "description": "Retreiving images of items.",
    },
    {
        "name": "Login and Registration",
        "description": "Routes for login and registration.",
    },
]

ENV_PATH: str = "./.env"
TITLE: str = "Awesome Store™️"
ROOT_PATH: str = ""
DOCS_URL: str = "/docs"
SUMMARY: str = "Awesome Store™️👌"
DESCRIPTION: str = """
# WE HAVE THE items
This API returns awesome items. **Enough said**.
<br>
![item](./static/store.gif)
"""
awesome_store_db: StoreDatabase = None


# ██      ██ ███████ ███████ ███████ ██████   █████  ███    ██     ███████ ██    ██ ███████ ███    ██ ████████
# ██      ██ ██      ██      ██      ██   ██ ██   ██ ████   ██     ██      ██    ██ ██      ████   ██    ██
# ██      ██ █████   █████   ███████ ██████  ███████ ██ ██  ██     █████   ██    ██ █████   ██ ██  ██    ██
# ██      ██ ██      ██           ██ ██      ██   ██ ██  ██ ██     ██       ██  ██  ██      ██  ██ ██    ██
# ███████ ██ ██      ███████ ███████ ██      ██   ██ ██   ████     ███████   ████   ███████ ██   ████    ██
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Opens connection to databse on startup.
    Close connection on shutdown.
    """
    load_dotenv(ENV_PATH)
    item_user: str = os.environ.get("STORE_USER")
    item_store_password = os.environ.get("STORE_PASSWORD")

    global awesome_store_db
    awesome_store_db = StoreDatabase(
        item_user, item_store_password, database="awesome_store", collection="items"
    )
    yield
    awesome_store_db.close()


# ███████  █████  ███████ ████████  █████  ██████  ██
# ██      ██   ██ ██         ██    ██   ██ ██   ██ ██
# █████   ███████ ███████    ██    ███████ ██████  ██
# ██      ██   ██      ██    ██    ██   ██ ██      ██
# ██      ██   ██ ███████    ██    ██   ██ ██      ██
app: FastAPI = FastAPI(
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    title=TITLE,
    root_path=ROOT_PATH,
    docs_url=DOCS_URL,
    summary=SUMMARY,
    description=DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Angel Badillo",
        "url": "https://thehonoredone.live",
        "email": "abadillo0224@mymsutexas.edu",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
# Specifying directory for static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ██████   ██████  ██    ██ ████████ ███████ ███████
# ██   ██ ██    ██ ██    ██    ██    ██      ██
# ██████  ██    ██ ██    ██    ██    █████   ███████
# ██   ██ ██    ██ ██    ██    ██    ██           ██
# ██   ██  ██████   ██████     ██    ███████ ███████
@app.get("/", tags=["/"])
async def docs_redirect():
    """Api's base route that displays the information about the API."""
    return RedirectResponse(url="/docs")


@app.get("/items", tags=["Items"])
def search_items(
    id: str = Query(None, description="ID of a item"),
    name: str = Query(None, description="Keyword in name of a item"),
    desc: str = Query(None, description="Keyword in description of item"),
    min_price: float = Query(
        0, description="Lower bound for price range of item", ge=0
    ),
    max_price: float = Query(
        1000000000000000,
        description="Highest bound for price range of item",
        ge=0,
        strict=False,
    ),
    category: str = Query(None, description="Category of item"),
    category_id: str = Query(None, description="Category id of item"),
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return", ge=0),
) -> dict:
    """
    Search for items based on a query string (e.g., name, category, flavor).
    """
    awesome_store_db.set_collection("items")

    query: dict = {}

    if isinstance(id, str):
        query["_id"] = StoreDatabase.str_to_object_id(id)
    if name:
        query["name"] = {"$regex": f"{name}", "$options": "i"}
    if desc:
        query["desc"] = {"$regex": f"{desc}", "$options": "i"}
    if category:
        query["category"] = category
    if isinstance(category_id, int):
        query["category_id"] = StoreDatabase.str_to_object_id(category_id)

    if max_price == None or min_price <= max_price:
        query["price"] = {"$gte": min_price, "$lte": max_price}

    item_list: list[dict] = awesome_store_db.find(query, skip=skip, limit=limit)

    return {"items": item_list}


@app.get("/item/category/{category_id}", tags=["Items"])
def item_by_category(
    category_id: str = Path(description="Category id of item"),
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return", ge=0),
) -> dict:
    """
    Get detailed information about items in a category by category ID.
    """
    awesome_store_db.set_collection("items")

    query: dict = {"category_id": StoreDatabase.str_to_object_id(category_id)}

    item_list: list[dict] = awesome_store_db.find(query, skip=skip, limit=limit)

    return {"items": item_list}


@app.get("/items/id/{item_id}", tags=["Items"])
def item_by_id(
    item_id: str = Path(..., description="The ID of the item to retrieve", ge=0)
):
    """
    Get detailed information about a specific item.
    """
    if not StoreDatabase.is_valid_object_id(item_id):
        return {"items": []}

    awesome_store_db.set_collection("items")
    item_list: list[dict] = list(
        awesome_store_db.find({"_id": StoreDatabase.str_to_object_id(item_id)})
    )
    return {"items": item_list}


@app.get("/image/{item_id}", tags=["Images"])
async def item_image(
    item_id: int = Path(..., description="The ID of the item to retrieve", ge=0)
):
    awesome_store_db.set_collection("items")
    item_list: list[dict] = list(awesome_store_db.find({"id": item_id}))

    if not item_list:
        return None

    img_url: str = item_list[0]["img_url"]
    file_name: str = item_list[0]["id"]
    image_response: requests.Response = requests.get(img_url)
    headers = {"Content-Language": "English", "Content-Type": "image/jpg"}
    headers["Content-Disposition"] = f"attachment;filename={file_name}.jpg"
    return Response(image_response.content, media_type="image/jpg", headers=headers)


@app.post("/items", tags=["Items"])
def add_new_item(
    item_info: Item = Body(description="For inserting a item record into the database"),
):
    """
    Add a new item to the store's inventory.
    """
    awesome_store_db.set_collection("categories")

    c_name: list[dict] = awesome_store_db.find({"name": item_info.category})

    # If existing category, just insert
    if c_name:
        awesome_store_db.set_collection("items")
        result = awesome_store_db.insert_one(dict(item_info))
        return result
    # If not existing category, create new category
    # Then insert new item
    else:
        awesome_store_db.set_collection("items")
        result = awesome_store_db.insert_one(dict(item_info))

        awesome_store_db.set_collection("categories")
        tempRes = awesome_store_db.insert_one({"name": item_info.category})

        return result


@app.put("/items/id/{item_id}", tags=["Items"])
def update_item_info(
    item_id: str = Path(..., description="The ID of the item to update."),
    item_info: Item = Body(description="For updating the information of a item."),
):
    """
    Update information about an existing item.
    """
    awesome_store_db.set_collection("items")

    query: dict = {}

    for key, val in dict(item_info).items():
        if not val is None:
            query[key] = val

    if StoreDatabase.is_valid_object_id(item_id):
        item_id = StoreDatabase.str_to_object_id(item_id)

    result: dict = awesome_store_db.update_one(
        {"_id": item_id}, {"$set": dict(item_info)}, upsert=True
    )

    return result


@app.delete("/items/{item_id}", tags=["Items"])
def delete_item(item_id: str):
    """
    Remove a item from the store's inventory.
    """
    awesome_store_db.set_collection("items")
    result = awesome_store_db.delete({"_id": StoreDatabase.str_to_object_id(item_id)})
    return result


@app.get("/categories", tags=["Categories"])
def all_categories():
    """
    Get a list of all item category information.
    """
    awesome_store_db.set_collection("categories")
    category_list: list[dict] = awesome_store_db.find({})
    return {"categories": category_list}


@app.post("/categories", tags=["Categories"])
def add_new_category(
    category: Category = Body(
        description="For inserting a new category into the database"
    ),
):
    """
    Insert a new category into the database.
    """
    awesome_store_db.set_collection("categories")

    exist = awesome_store_db.find(dict(category), limit=1)
    if exist:
        return {
            "acknowledged": True,
            "inserted_id": "None",
        }
    result: dict = awesome_store_db.insert_one(dict(category))

    return result


@app.get("/categories/id/{category_id}", tags=["Categories"])
def category_by_id(
    category_id: int = Path(
        ..., description="The ID of the category information to retrieve"
    )
):
    """
    Get the information of a item category by ID.
    """
    awesome_store_db.set_collection("categories")
    category_list: list[dict] = awesome_store_db.find({"id": category_id}, {"_id": 0})
    return {"categories": category_list}


if __name__ == "__main__":
    load_dotenv(ENV_PATH)

    HOST: str = "0.0.0"
    PORT: int = 8085
    ssl_certfile: str = os.environ.get("SSL_CERTFILE")
    ssl_keyfile: str = os.environ.get("SSL_KEYFILE")
    ssl_ca_certs: str = os.environ.get("SSL_CA_CERTS")

    uvicorn.run(
        "api:app",
        host=HOST,
        port=PORT,
        log_level="debug",
        reload=True,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        ssl_ca_certs=ssl_ca_certs,
    )
