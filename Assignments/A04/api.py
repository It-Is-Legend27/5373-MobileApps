"""Candy Store API

Candy Store API built with FastAPI.

"""

from fastapi import FastAPI, Query, Path, Body
from fastapi.responses import RedirectResponse, FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mongoManager import MongoManager
from contextlib import asynccontextmanager
import uvicorn
import json
import os
from rich import print
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import requests


# ██████   █████  ███████ ███████     ███    ███  ██████  ██████  ███████ ██      ███████
# ██   ██ ██   ██ ██      ██          ████  ████ ██    ██ ██   ██ ██      ██      ██
# ██████  ███████ ███████ █████       ██ ████ ██ ██    ██ ██   ██ █████   ██      ███████
# ██   ██ ██   ██      ██ ██          ██  ██  ██ ██    ██ ██   ██ ██      ██           ██
# ██████  ██   ██ ███████ ███████     ██      ██  ██████  ██████  ███████ ███████ ███████
class Candy(BaseModel):
    """
    Provides JSON-schema for a "candy" object / entry.
    """

    id: int = Field(description="The ID of a candy.")
    name: str = Field(None, description="The name of a candy.")
    prod_url: str = Field(None, description="The product url of a candy.")
    img_url: str = Field(None, description="The image url of a candy.")
    price: float = Field(None, description="The price of a candy.")
    desc: str = Field(None, description="The description of a candy.")
    category: str = Field(None, description="The category name of a candy.")
    category_id: int = Field(None, description="The category ID of a candy.")


class Category(BaseModel):
    """
    Provides JSON-schema for a "category" object / entry.
    """

    name: str = Field(description="The name of a category.")
    id: int = Field(description="The ID of a category.")


TAGS_METADATA: list[dict[str, str]] = [
    {
        "name": "/",
        "description": "Redirects to the docs.",
    },
    {
        "name": "Candies",
        "description": "Operations with candies.",
    },
    {
        "name": "Categories",
        "description": "Operations with categories.",
    },
    {
        "name": "Images",
        "description": "Retrieves image of candy by ID.",
    },
]

ENV_PATH: str = "./.env"
TITLE: str = "Candy Store™️"
ROOT_PATH: str = ""
DOCS_URL: str = "/docs"
SUMMARY: str = "Candy Store™️👌"
DESCRIPTION: str = """
# WE HAVE THE CANDIES
This API returns candy store stuff. **Enough said**.
<br>
![candy](./static/candy_face.gif)
"""
candy_store_db: MongoManager = None


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
    candy_user: str = os.environ.get("CANDY_STORE_USER")
    candy_store_password = os.environ.get("CANDY_STORE_PASSWORD")

    global candy_store_db
    candy_store_db = MongoManager(
        candy_user, candy_store_password, database="candy_store", collection="candies"
    )
    yield
    candy_store_db.close()


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
    """Api's base route that displays the information created above in the ApiInfo section."""
    return RedirectResponse(url="/docs")


@app.get("/candies", tags=["Candies"])
def search_candies(
    id: int = Query(None, description="ID of a candy", ge=0),
    name: str = Query(None, description="Keyword in name of a candy"),
    desc: str = Query(None, description="Keyword in description of candy"),
    min_price: float = Query(
        0, description="Lower bound for price range of candy", ge=0
    ),
    max_price: float = Query(
        1000000000000000,
        description="Highest bound for price range of candy",
        ge=0,
        strict=False,
    ),
    category: str = Query(None, description="Category of candy"),
    category_id: int = Query(None, description="Category id of candy", ge=0),
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return"),
) -> dict:
    """
    Search for candies based on a query string (e.g., name, category, flavor).
    """
    candy_store_db.setCollection("candies")

    query: dict = {}

    if isinstance(id, int):
        query["id"] = id
    if name:
        query["name"] = {"$regex": f"{name}", "$options": "i"}
    if desc:
        query["desc"] = {"$regex": f"{desc}", "$options": "i"}
    if category:
        query["category"] = category
    if isinstance(category_id, int):
        query["category_id"] = category_id

    if max_price == None or min_price <= max_price:
        query["price"] = {"$gte": min_price, "$lte": max_price}

    candy_list: list[dict] = candy_store_db.get(
        query, {"_id": 0}, skip=skip, limit=limit
    )

    return {"candies": candy_list}


@app.get("/candies/category/{category_id}", tags=["Candies"])
def candy_by_category(
    category_id: int = Path(description="Category id of candy", ge=0),
    skip: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(0, description="Limits the number of items to return"),
) -> dict:
    """
    Get detailed information about candies in a category by category ID.
    """
    candy_store_db.setCollection("candies")

    query: dict = {"category_id": category_id}

    candy_list: list[dict] = candy_store_db.get(
        query, {"_id": 0}, skip=skip, limit=limit
    )

    return {"candies": candy_list}


@app.get("/candies/id/{candy_id}", tags=["Candies"])
def candy_by_id(
    candy_id: int = Path(..., description="The ID of the candy to retrieve", ge=0)
):
    """
    Get detailed information about a specific candy.
    """
    candy_store_db.setCollection("candies")
    candy_list: list[dict] = list(candy_store_db.get({"id": candy_id}))
    return {"candies": candy_list}


@app.get("/candies/id/{candy_id}/image", tags=["Images"])
async def candy_image(
    candy_id: int = Path(..., description="The ID of the candy to retrieve", ge=0)
):
    candy_store_db.setCollection("candies")
    candy_list: list[dict] = list(candy_store_db.get({"id": candy_id}))

    if not candy_list:
        return None

    img_url: str = candy_list[0]["img_url"]
    file_name: str = candy_list[0]["id"]
    image_response: requests.Response = requests.get(img_url)
    headers = {"Content-Language": "English", "Content-Type": "image/jpg"}
    headers["Content-Disposition"] = f"attachment;filename={file_name}.jpg"
    return Response(image_response.content, media_type="image/jpg", headers=headers)


@app.post("/candies", tags=["Candies"])
def add_new_candy(
    candy_info: Candy = Body(
        description="For inserting a candy record into the database"
    ),
):
    """
    Add a new candy to the store's inventory.
    """
    candy_store_db.setCollection("candies")

    candy: list[dict] = candy_store_db.get({"id": candy_info.id})

    # If existing candy, do nothing
    if candy:
        return {"acknowledge": False, "inserted_ids": []}

    candy_store_db.setCollection("categories")

    c_id: list[dict] = candy_store_db.get({"id": candy_info.category_id}, {"_id": 1})
    c_name: list[dict] = candy_store_db.get({"name": candy_info.category}, {"_id": 1})

    if c_id and c_name:
        # If existing category, just insert
        if c_id[0]["_id"] == c_name[0]["_id"]:
            candy_store_db.setCollection("candies")
            result = candy_store_db.post(dict(candy_info))
            return result
        # If _id do not match
        else:
            return {"acknowledge": False, "inserted_ids": []}
    # If one or other list is empty, do nothing
    elif (c_id and not c_name) or (not c_id and c_name):
        return {"acknowledge": False, "inserted_ids": []}
    # If not existing category, create new category
    # Then insert new candy
    else:
        candy_store_db.setCollection("candies")
        result = candy_store_db.post(dict(candy_info))

        candy_store_db.setCollection("categories")
        tempRes = candy_store_db.post(
            {"name": candy_info.category, "id": candy_info.category_id}
        )

        result["inserted_ids"] += tempRes["inserted_ids"]
        return result


@app.put("/candies", tags=["Candies"])
def update_candy_info(
    candy_info: Candy = Body(description="For updating the information of a candy."),
):
    """
    Update information about an existing candy.
    """
    candy_store_db.setCollection("candies")

    query: dict = {}

    for key, val in dict(candy_info).items():
        if key == "id":
            continue
        if not val is None:
            query[key] = val

    result: dict = candy_store_db.put("id", candy_info.id, query)

    return result


@app.delete("/candies/id/{candy_id}", tags=["Candies"])
def delete_candy(candy_id: int):
    """
    Remove a candy from the store's inventory.
    """
    candy_store_db.setCollection("candies")
    result = candy_store_db.delete({"id": candy_id})
    return result


@app.get("/categories", tags=["Categories"])
def all_categories():
    """
    Get a list of all candy category information.
    """
    candy_store_db.setCollection("categories")
    category_list: list[dict] = candy_store_db.get({}, {"_id": 0})
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
    candy_store_db.setCollection("categories")
    c_id: list[dict] = candy_store_db.get({"id": category.id}, {"_id": 1})
    c_name: list[dict] = candy_store_db.get({"id": category.id}, {"_id": 1})

    if c_id and c_name:
        # If existing category
        if c_id[0]["_id"] == c_name[0]["_id"]:
            return {"acknowledge": False, "inserted_ids": []}
        # If _id do not match, return None
        else:
            return {"acknowledge": False, "inserted_ids": []}
    # If one or other list is empty, do nothing
    elif (c_id and not c_name) or (not c_id and c_name):
        return {"acknowledge": False, "inserted_ids": []}
    # If not existing category, create new category
    # Then insert new category
    else:
        result = candy_store_db.post({"name": category.name, "id": category.name})
        return result


@app.get("/categories/id/{category_id}", tags=["Categories"])
def category_by_id(
    category_id: int = Path(
        ..., description="The ID of the category information to retrieve"
    )
):
    """
    Get the information of a candy category by ID.
    """
    candy_store_db.setCollection("categories")
    category_list: list[dict] = candy_store_db.get({"id": category_id}, {"_id": 0})
    return {"categories": category_list}


if __name__ == "__main__":
    load_dotenv(ENV_PATH)

    HOST: str = "0.0.0"
    PORT: int = 8084
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
