# Libraries for FastAPI
from fastapi import FastAPI, Query, Path, Body
from fastapi.responses import RedirectResponse, FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mongoManager import MongoManager
from contextlib import asynccontextmanager
import uvicorn
import json
import ssl
import os
import sys
from rich import print
from dotenv import load_dotenv

ENV_PATH: str = "./.env"
TITLE: str = "Candy Store™️"
HOST: str = "0.0.0"
PORT: int = 8080
ROOT_PATH: str = ""
DOCS_URL: str = "/docs"
SUMMARY: str = "Candy Store™️👌"
DESCRIPTION: str = """
# WE HAVE THE CANDIES
This API returns candy store stuff. **Enough said**.
"""
candy_store_db: MongoManager = None

# Needed for CORS
# origins = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(ENV_PATH)
    CANDY_USER: str = os.environ.get("CANDY_STORE_USER")
    CANDY_STORE_PASSWORD = os.environ.get("CANDY_STORE_PASSWORD")

    global candy_store_db
    candy_store_db = MongoManager(
        CANDY_USER, CANDY_STORE_PASSWORD, database="candy_store", collection="candies"
    )
    yield
    candy_store_db.close()


app: FastAPI = FastAPI(
    lifespan=lifespan,
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
app.mount("/static", StaticFiles(directory="static"), name="static")
# Needed for CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# Routes
@app.get("/")
async def docs_redirect():
    """Api's base route that displays the information created above in the ApiInfo section."""
    return RedirectResponse(url="/docs")


@app.get("/candies")
def all_candies():
    """
    Retrieve a list of all candies available in the store.
    """
    candy_store_db.setCollection("candies")
    candy_list: list[dict] = candy_store_db.get({}, {"_id": 0})
    return {"candies": candy_list}


@app.get("/candies/search")
def search_candies(
    id:int = Query(None, description="ID of a candy"),
    name:str = Query(None, description="Keyword in name of a candy"),
    desc:str = Query(None, description="Keyword in description of candy"),
    min_price:float = Query(0, description="Lower bound for price range of candy", ge=0),
    max_price:float = Query(1000000000000000, description="Highest bound for price range of candy", ge=0, strict=False),
    category:str = Query(None, description="Category of candy"),
    category_id:int = Query(None, description="Category id of candy")
):
    """
    Search for candies based on a query string (e.g., name, category, flavor).
    """
    candy_store_db.setCollection("candies")

    query:dict = {}

    if id:
        query["id"] = id
    if name:
        query["name"] = {"$regex" : f"{name}", "$options": "i"}
    if desc:
        query["desc"] = {"$regex" : f"{desc}", "$options": "i"}
    if category:
        query["category"] = category
    if category_id:
        query["category_id"] = category_id
    
    if max_price == None or min_price <= max_price:
        query["price"] = {"$gte": min_price, "$lte": max_price}

    candy_list: list[dict] = candy_store_db.get(query, {"_id": 0})

    return {"candies": candy_list, "query": 1}


@app.get("/candies/id/{candy_id}")
def candy_by_id(
    candy_id: int = Path(..., description="The ID of the candy to retrieve")
):
    """
    Get detailed information about a specific candy.
    """
    candy_list: list[dict] = list(candy_store_db.get({"id": candy_id}))
    return {"candies": candy_list}


@app.post("/candies")
def add_new_candy():
    """
    Add a new candy to the store's inventory.
    """
    pass


@app.put("/candies/id/{candy_id}")
def update_candy_info(candy_id: int):
    """
    Update information about an existing candy.
    """
    pass


@app.delete("/candies/id/{candy_id}")
def delete_candy(candy_id: int):
    """
    Remove a candy from the store's inventory.
    """
    pass


@app.get("/categories")
def all_categories():
    """
    Get a list of all candy category information.
    """
    candy_store_db.setCollection("categories")
    category_list: list[dict] = candy_store_db.get({}, {"_id": 0})
    return {"categories": category_list}

@app.get("/categories/id/{category_id}")
def category_by_id(
    category_id: int = Path(..., description="The ID of the category information to retrieve")
):
    """
    Get the information of a candy category by ID.
    """
    candy_store_db.setCollection("categories")
    category_list: list[dict] = candy_store_db.get({"id": category_id}, {"_id": 0})
    return {"categories": category_list}

"""
This main block gets run when you invoke this file. How do you invoke this file?

        python api.py 

After it is running, copy paste this into a browser: http://127.0.0.1:8080 

You should see your api's base route!

Note:
    Notice the first param below: api:app 
    The left side (api) is the name of this file (api.py without the extension)
    The right side (app) is the bearingiable name of the FastApi instance declared at the top of the file.
"""
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=HOST,
        port=PORT,
        log_level="debug",
        reload=True,
        ssl_certfile="/home/angel/thehonoredone_certs/thehonoredone.live.crt",
        ssl_keyfile="/home/angel/thehonoredone_certs/thehonoredone.live.key",
    )
