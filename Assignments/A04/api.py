# Libraries for FastAPI
from fastapi import FastAPI, Query, Path
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json


TITLE:str = "Candy Store"
HOST:str = "0.0.0"
PORT:int = 8080
ROOT_PATH:str = ""
DOCS_URL:str = "/docs"
SUMMARY:str = "Summary"
DESCRIPTION:str = "Description"

# Needed for CORS
# origins = ["*"]

app:FastAPI = FastAPI(
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
def list_all_candies():
    """
    Retrieve a list of all candies available in the store.
    """
    pass


@app.get("/candies/search")
def search_candies(
    query: str = Query(None, description="Query string to search candies")
):
    """
    Search for candies based on a query string (e.g., name, category, flavor).
    """
    pass


@app.get("/candies/{candy_id}")
def get_candy_details(
    candy_id: int = Path(..., description="The ID of the candy to retrieve")
):
    """
    Get detailed information about a specific candy.
    """
    pass


@app.post("/candies")
def add_new_candy():
    """
    Add a new candy to the store's inventory.
    """
    pass


@app.put("/candies/{candy_id}")
def update_candy_info(candy_id: int):
    """
    Update information about an existing candy.
    """
    pass


@app.delete("/candies/{candy_id}")
def delete_candy(candy_id: int):
    """
    Remove a candy from the store's inventory.
    """
    pass


@app.get("/categories")
def list_categories():
    """
    Get a list of candy categories (e.g., chocolates, gummies, hard candies).
    """
    pass


@app.get("/promotions")
def promotions_and_deals():
    """
    Information about current promotions, deals, or discounts.
    """
    pass


@app.get("/store-info")
def store_information():
    """
    Basic information about the candy store, including contact details.
    """
    pass


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
    uvicorn.run("api:app", host=HOST, port=PORT, log_level="debug", reload=True)
