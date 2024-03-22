"""
This file opens up the folder categoryJson and processes each json file
adding the category name to each candy document and posting it to mongodb
"""

from mongoManager import CandyStoreDB
import json
import glob
from rich import print
from dotenv import load_dotenv
import os

def load_database(
    folder_path: str = "./",
    username: str = None,
    password: str = None,
    host: str = None,
    port: str = None,
    database: str = None,
    candy_collection: str = None,
    categories_collection: str = None,
) -> None:

    # Get absolute path
    folder_path = os.path.abspath(folder_path)

    # Get list of paths to all json files
    json_files = glob.glob(f"{folder_path}/*.json")

    db = CandyStoreDB(
        username=username, password=password, host=host, port=port, database=database
    )

    db.setCollection(candy_collection)

    db.dropCollection(candy_collection)

    db.setCollection(categories_collection)

    db.dropCollection(categories_collection)

    i = 0

    for file in json_files:
        parts = file.split("/")
        category = parts[-1][:-5].replace("-", " ").title()

        summary:dict = {}

        with open(file) as f:
            data:dict = json.load(f)

            summary["name"] = category
            summary["id"] = int(i)

            for id, item in data.items():
                item["id"] = int(id)
                item["category"] = category
                item["category_id"] = int(i)
                db.setCollection("candies")

                if not db.get({"id": item["id"]}):
                    db.post(item)
        db.setCollection("categories")
        db.post(summary)
        i += 1


if __name__ == "__main__":
    
    ENV_PATH:str = "./.env"

    load_dotenv(ENV_PATH)

    username:str = os.environ.get("CANDY_STORE_USER")
    password:str = os.environ.get("CANDY_STORE_PASSWORD")

    kwargs = {
        "folder_path": "./categoryJson",
        "username": username,
        "password": password,
        "database": "candy_store",
        "candy_collection": "candies",
        "categories_collection": "categories",
        "port": 27017,
        "host": "localhost",
    }

    load_database(**kwargs)
