"""Awesome Store API

Awesome Store API built with FastAPI.
"""

from fastapi import FastAPI, Query, Path, Body
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from store_database import StoreDatabase
from pymongo.errors import PyMongoError, ProtocolError, DuplicateKeyError
from contextlib import asynccontextmanager
import uvicorn
import json
import os
from rich import print
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import requests
from models import Item, User


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
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return", ge=0),
) -> dict:
    """
    Search for items based on a query string (e.g., name, category, flavor).
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    query: dict = {}

    try:
        if id:
            if StoreDatabase.is_valid_object_id(id):
                query["_id"] = StoreDatabase.str_to_object_id(id)
            else:
                query["_id"] = id
        if name:
            query["name"] = {"$regex": f"{name}", "$options": "i"}
        if desc:
            query["desc"] = {"$regex": f"{desc}", "$options": "i"}
        if category:
            query["category"] = category

        if max_price == None or min_price <= max_price:
            query["price"] = {"$gte": min_price, "$lte": max_price}

        item_list: list[dict] = awesome_store_db.find(query, skip=skip, limit=limit)
        return {"items": item_list}
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.get("/items/category/{category}", tags=["Items"])
def item_by_category(
    category: str = Path(description="Category name of item"),
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return", ge=0),
) -> dict:
    """
    Get detailed information about items in a category by category name.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    query: dict = {"category": category}

    try:
        item_list: list[dict] = awesome_store_db.find(query, skip=skip, limit=limit)

        return {"items": item_list}
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.get("/items/id/{id}", tags=["Items"])
def item_by_id(id: str = Path(..., description="The ID of the item to retrieve")):
    """
    Get detailed information about a specific item.
    """
    if not StoreDatabase.is_valid_object_id(id):
        raise HTTPException(404, detail="Not Found")

    try:
        awesome_store_db.set_collection("items")
        item: dict | None = awesome_store_db.find_one(
            {"_id": StoreDatabase.str_to_object_id(id)}
        )

        return {"item": item}
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.get("/image/{id}", tags=["Images"])
async def item_image(id: str = Path(..., description="The ID of the item to retrieve")):
    """
    Get an item's image, given the ID.
    """
    awesome_store_db.set_collection("items")

    if not StoreDatabase.is_valid_object_id(id):
        raise HTTPException(404, detail="Not Found")

    item: dict = awesome_store_db.find_one({"_id": StoreDatabase.str_to_object_id(id)})

    if not item:
        raise HTTPException(404, detail="Not Found")

    try:
        img_url: str = item["img_url"]
        file_name: str = item["_id"]
        image_response: requests.Response = requests.get(img_url)
        headers = {"Content-Language": "English", "Content-Type": "image/jpg"}
        headers["Content-Disposition"] = f"attachment;filename={file_name}.jpg"
        return Response(image_response.content, media_type="image/jpg", headers=headers)
    except Exception as e:
        raise HTTPException(400, f"{e}")


@app.post("/items", tags=["Items"])
def add_new_item(
    item: Item = Body(description="For inserting a item record into the database"),
):
    """
    Add a new item to the store's inventory.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    try:
        result: dict = awesome_store_db.insert_one(dict(item))
        return result
    except Exception as e:
        raise HTTPException(400, f"{e}")


@app.put("/items/id/{id}", tags=["Items"])
def update_item_info(
    id: str = Path(..., description="The ID of the item to update."),
    item_info: Item = Body(description="For updating the information of a item."),
):
    """
    Update information about an existing item. If item does not exist, insert new one.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    if not StoreDatabase.is_valid_object_id(id):
        raise HTTPException(404, detail="Not Found")
    try:
        result: dict = awesome_store_db.update_one(
            {"_id": StoreDatabase.str_to_object_id(id)},
            {"$set": dict(item_info)},
            upsert=True,
        )

        return result
    except Exception as e:
        raise HTTPException(400, detail=f"{e}")


@app.delete("/items/{id}", tags=["Items"])
def delete_item(id: str = Path(..., description="The ID of the item to retrieve")):
    """
    Remove a item from the store's inventory.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    if not StoreDatabase.is_valid_object_id(id):
        print("Whoosh")
        raise HTTPException(404, detail="Not Found")

    try:
        result: dict = awesome_store_db.delete_one(
            {"_id": StoreDatabase.str_to_object_id(id)}
        )
        return result
    except Exception as e:
        raise HTTPException(400, f"{e}")


@app.get("/categories", tags=["Categories"])
def all_categories():
    """
    Get a list of all item category information.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    try:
        category_list: list[dict] = awesome_store_db.distinct("category")
        return {"categories": category_list}
    except Exception as e:
        raise HTTPException(400, f"{e}")


@app.post("/login", tags=["Login and Registration"])
def login(
    username: str = Body(description="Username of user."),
    password: str = Body(description="Password of user."),
):
    """
    Logging into the app.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.UsersCollection)

    try:
        result: dict = awesome_store_db.find_one({"username": username})

        if not result:
            return {"success": False, "detail": "Username does not exist."}

        result = dict(result)

        success: bool = result.get("password") == password

        if success:
            return {"success": success, "detail": "Login successful"}
        else:
            return {"success": False, "detail": "Incorrect password"}

    except Exception as e:
        raise HTTPException(400, f"{e}")


@app.post("/register", tags=["Login and Registration"])
def register(user: User = Body(description="User information")):
    """
    Registering as a new user for the app.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.UsersCollection)

    try:
        result: dict = awesome_store_db.insert_one(dict(user))

        return {"success": True, "detail": "Registration successful."}
    except DuplicateKeyError as d:
        return {
            "success": False,
            "detail": "Username or email is already in use. Use a different username or email address.",
        }
    except Exception as e:
        raise HTTPException(400, f"{e}")


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
