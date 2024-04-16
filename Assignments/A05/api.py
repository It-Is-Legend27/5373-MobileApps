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
from models import Item, User, Location
from hashlib import sha256
from email_validator import ValidatedEmail, validate_email, EmailNotValidError
import re


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
    {
        "name": "Users",
        "description": "Operations with user data.",
    },
    {
        "name": "Locations",
        "description": "Operations with user locations.",
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
    tags: list[str] = Query(None, description="Tags associated with the item"),
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return", ge=0),
) -> dict:
    """
    Search for items based on a query string (e.g., name, category, tags).
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    query: dict = {}

    try:
        if id != None:
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
        if tags:
            query["tags"] = {"$in": tags}

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


@app.get("/image/id/{id}", tags=["Images"])
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


@app.delete("/items/id/{id}", tags=["Items"])
def delete_item(id: str = Path(..., description="The ID of the item to retrieve")):
    """
    Remove a item from the store's inventory.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.ItemsCollection)

    if not StoreDatabase.is_valid_object_id(id):
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
    try:
        category_list: list[dict] = [
            str(category) for category in StoreDatabase.Categories
        ]
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
        # Hashing password
        encoded_str: bytes = password.encode()
        hashed_password: str = sha256(encoded_str).hexdigest()

        result: dict = awesome_store_db.find_one({"username": username})

        if not result:
            return {"success": False, "detail": "Username does not exist"}

        result = dict(result)

        success: bool = result.get("password") == hashed_password

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
        name_pattern = re.compile(r"^[A-Z]([a-zA-z]*)(([ -])?[A-Z]([a-zA-z]*))*$")

        # Data validation
        if not name_pattern.match(user.first_name):
            raise Exception(
                "Invalid first name. Must consist of alphabetic characters. Cannot be empty string"
            )
        if not name_pattern.match(user.last_name):
            raise Exception(
                "Invalid first name. Must consist of alphabetic characters. Cannot be empty string"
            )
        if not user.password.isalnum():
            raise Exception(
                "Invalid password. Must consist of alpah-numeric characters. Cannot be empty string"
            )

        # Validate email
        emailinfo: ValidatedEmail = validate_email(user.email)

        encoded_str: bytes = user.password.encode()
        user.password = sha256(encoded_str).hexdigest()
        result: dict = awesome_store_db.insert_one(dict(user))

        return {"success": True, "detail": "Registration successful"}
    except EmailNotValidError as e:
        return {
            "success": False,
            "detail": "Invalid email address. Please enter a valid email address.",
        }
    except DuplicateKeyError as d:
        return {
            "success": False,
            "detail": "Username or email is already in use. Use a different username or email address",
        }
    except Exception as e:
        return {"success": False, "detail": f"{e}"}


@app.get("/users", tags=["Users"])
def get_all_user_data():
    try:
        awesome_store_db.set_collection(StoreDatabase.Collections.UsersCollection)

        users: list[dict] = awesome_store_db.find({}, {"_id": 0, "password": 0})

        # If user is found, return user data
        return {"users": users}
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.get("/users/username/{username}", tags=["Users"])
def get_user_data(username: str = Path(..., description="The username of the user.")):
    """
    Returns user data for a given user.
    """
    try:
        awesome_store_db.set_collection(StoreDatabase.Collections.UsersCollection)

        user: dict | None = awesome_store_db.find_one(
            {"username": username}, {"_id": 0, "password": 0}
        )

        # If user is not found, report 404
        if user is None:
            raise HTTPException(404, detail="Not Found")

        # If user is found, return user data
        return {"user": user}
    except HTTPException as h:
        raise HTTPException(404, detail="Not Found")
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.put("/users/username/{username}", tags=["Users"])
def update_user_data(
    username: str = Path(..., description="The username of the user."),
    first_name: str = Body(description="The first name of a user."),
    last_name: str = Body(description="The last name of a user."),
    email: str = Body(description="The email of a user."),
    password: str = Body(description="The password of a user."),
):
    """
    Update the user data of a given user.
    """
    try:
        awesome_store_db.set_collection(StoreDatabase.Collections.UsersCollection)

        name_pattern = re.compile(r"^[A-Z]([a-zA-z]*)(([ -])?[A-Z]([a-zA-z]*))*$")

        # Data validation
        if not name_pattern.match(first_name):
            raise Exception(
                "Invalid first name. Must consist of alphabetic characters. Cannot be empty string"
            )
        if not name_pattern.match(last_name):
            raise Exception(
                "Invalid first name. Must consist of alphabetic characters. Cannot be empty string"
            )
        if not password.isalnum():
            raise Exception(
                "Invalid password. Must consist of alpah-numeric characters. Cannot be empty string"
            )

        # Validate email
        emailinfo: ValidatedEmail = validate_email(email)

        encoded_str: bytes = password.encode()
        password = sha256(encoded_str).hexdigest()

        result: dict = awesome_store_db.update_one(
            {"username": username},
            {"$set": {"email": email, "password": password}},
            upsert=False,
        )

        return result
    except Exception as e:
        raise HTTPException(400, detail=f"{e}")


# @app.delete("/users/username/{username}", tags=["Users"])
# def remove_user_data(
#     username: str = Path(..., description="The username of the user.")
# ):
#     """
#     Remove a user's data from the user collection.
#     """
#     try:
#         awesome_store_db.set_collection(StoreDatabase.Collections.UsersCollection)

#         result: dict = awesome_store_db.delete_one({"username": username})
#         return result
#     except Exception as e:
#         raise HTTPException(400, f"{e}")


@app.get("/locations", tags=["Locations"])
def get_all_location_data():
    try:
        awesome_store_db.set_collection(StoreDatabase.Collections.LocationsCollection)

        locations: list[dict] = awesome_store_db.find({}, {"_id": 0})

        # If user is found, return user data
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.get("/locations/username/{username}", tags=["Locations"])
def get_location_data(
    username: str = Path(..., description="The username of the user.")
):
    """
    Returns location data for a given user.
    """
    try:
        awesome_store_db.set_collection(StoreDatabase.Collections.LocationsCollection)

        location: dict | None = awesome_store_db.find_one(
            {"username": username}, {"_id": 0}
        )

        # If user is not found, report 404
        if location is None:
            raise HTTPException(404, detail="Not Found")

        # If user is found, return user data
        return {"location": location}
    except HTTPException as h:
        raise HTTPException(404, detail="Not Found")
    except Exception as e:
        raise HTTPException(422, f"{e}")


@app.put("/locations/username/{username}", tags=["Locations"])
def update_location_data(
    username: str = Path(..., description="The username of the user."),
    latitude: float = Body(description="The latitude of the user."),
    longitude: float = Body(description="The longitude of the user."),
    timestamp: int = Body(
        description="The UNIX timestamp in milliseconds when the location was received."
    ),
):
    """
    Update the location data of a given user.
    """
    try:
        awesome_store_db.set_collection(StoreDatabase.Collections.LocationsCollection)

        result: dict = awesome_store_db.update_one(
            {"username": username},
            {
                "$set": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": timestamp,
                }
            },
            upsert=True,
        )

        return result
    except Exception as e:
        raise HTTPException(400, detail=f"{e}")


# @app.delete("/locations/username/{username}", tags=["Locations"])
# def remove_location_data(
#     username: str = Path(..., description="The username of the user.")
# ):
#     """
#     Remove a user's location data from the locations collection.
#     """
#     try:
#         awesome_store_db.set_collection(StoreDatabase.Collections.LocationsCollection)

#         result: dict = awesome_store_db.delete_one({"username": username})
#         return result
#     except Exception as e:
#         raise HTTPException(400, f"{e}")


@app.post("/locations", tags=["Locations"])
def post_location_data(
    location: Location = Body(
        description="For inserting a item record into the database"
    ),
):
    """
    Add a new user's location to the location collection.
    """
    awesome_store_db.set_collection(StoreDatabase.Collections.LocationsCollection)

    try:
        result: dict = awesome_store_db.insert_one(dict(location))
        return result
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
