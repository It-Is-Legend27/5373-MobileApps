"""
This file opens up the folder categoryJson and processes each json file
adding the category name to each candy document and posting it to mongodb
"""

from store_database import StoreDatabase
import json
import glob
from rich import print
from dotenv import load_dotenv
import os


def load_database(
    folder_path: str = "./",
    collection_validator_config: str = "./collection_validators.json",
    users_file: str = "./users.json",
    username: str = None,
    password: str = None,
    host: str = None,
    port: str = None,
    database: str = None,
    items_collection: (
        str | StoreDatabase.Collections
    ) = StoreDatabase.Collections.UsersCollection,
    categories_collection: (
        str | StoreDatabase.Collections
    ) = StoreDatabase.Collections.CategoriesCollection,
    users_collection: (
        str | StoreDatabase.Collections
    ) = StoreDatabase.Collections.UsersCollection,
) -> None:

    # Get absolute path
    folder_path = os.path.abspath(folder_path)

    # Get list of paths to all json files
    json_files = glob.glob(f"{folder_path}/*.json")

    validators: dict = None
    users: list[dict] = None

    with open(collection_validator_config, "r") as file:
        validators = json.load(file)

    db = StoreDatabase(
        username=username, password=password, host=host, port=port, database=database
    )

    db.drop_collection(items_collection)
    db.drop_collection(categories_collection)
    db.drop_collection(users_collection)

    db.create_collection(items_collection, validators[items_collection])
    db.create_collection(
        categories_collection, validators[categories_collection]
    )
    db.create_collection(users_collection, validators[users_collection])

    with open(users_file, "r") as file:
        users = json.load(file)

    db.set_collection(StoreDatabase.Collections.UsersCollection)
    db.insert_many(users)

    for file in json_files:
        parts = file.split("/")
        category_name = parts[-1][:-5].replace("-", " ").title()

        category: dict = {}

        with open(file) as f:
            json_data: dict = json.load(f)

            category["name"] = category_name
            db.set_collection(categories_collection)
            result: dict = db.insert_one(category)
            category["_id"] = StoreDatabase.str_to_object_id(result["inserted_id"])

            db.set_collection(items_collection)
            for id, item in json_data.items():
                item["category_name"] = category["name"]
                item["category_id"] = category["_id"]
                if not db.find({"name": item["name"]}):
                    db.insert_one(item)


if __name__ == "__main__":

    ENV_PATH: str = "./.env"

    load_dotenv(ENV_PATH)

    username: str = os.environ.get("STORE_USER")
    password: str = os.environ.get("STORE_PASSWORD")

    kwargs = {
        "folder_path": "./categoryJson",
        "username": username,
        "password": password,
        "database": "awesome_store",
        "items_collection": StoreDatabase.Collections.ItemsCollection,
        "categories_collection": StoreDatabase.Collections.CategoriesCollection,
        "port": 27017,
        "host": "localhost",
    }

    load_database(**kwargs)
