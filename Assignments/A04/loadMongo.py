"""
This file opens up the folder categoryJson and processes each json file
adding the category name to each candy document and posting it to mongodb
"""

from mongoManager import MongoManager
import json
import glob
from rich import print
import sys
import os


def load(
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

    db = MongoManager(
        username=username, password=password, host=host, port=port, database=database
    )

    db.setCollection(candy_collection)

    db.dropCollection(candy_collection)

    db.setCollection(categories_collection)

    db.dropCollection(categories_collection)

    i = 0

    for file in json_files:

        print(file)
        parts = file.split("/")
        category = parts[-1][:-5].replace("-", " ").title()

        print(category)

        summary = {}

        with open(file) as f:
            data = json.load(f)

            summary["count"] = len(data)
            summary["name"] = category
            summary["id"] = i

            for id, item in data.items():
                item["category"] = category
                item["category_id"] = i
                print(item)
                db.setCollection("candies")
                db.post(item)
        db.setCollection("categories")
        db.post(summary)
        i += 1


if __name__ == "__main__":

    kwargs = {
        "folder_path": "./Assignments/A04/categoryJson",
        "username": "angel",
        "password": "aB_1618401m",
        "database": "candy_store",
        "candy_collection": "candies",
        "categories_collection": "categories",
        "port": 27017,
        "host": "localhost",
    }

    load(**kwargs)
