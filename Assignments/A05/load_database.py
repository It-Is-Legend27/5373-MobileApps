"""Setting up and populating the database.

Provides function for easily initializing and creating the store database.
Provides the function load_database.
"""

from store_database import StoreDatabase
import json
import glob
from rich import print
from dotenv import load_dotenv
import os
from hashlib import sha256


def load_database(
    folder_path: str = "./",
    collection_validator_config: str = "./collection_validators.json",
    users_file: str = "./users.json",
    username: str = None,
    password: str = None,
    host: str = None,
    port: str = None,
    database: str = None,
) -> None:
    """Configures the database and populates the collections.

    Configures the database for the store and populates the collections.
    """
    # Get absolute path
    folder_path = os.path.abspath(folder_path)

    # Get list of paths to all json files
    json_files = glob.glob(f"{folder_path}/*.json")

    validators: dict = None
    users: list[dict] = None

    # Read in validator / jsonSchema for each collection
    with open(collection_validator_config, "r") as file:
        validators = json.load(file)

    db = StoreDatabase(
        username=username, password=password, host=host, port=port, database=database
    )

    db.drop_collection(StoreDatabase.Collections.ItemsCollection)
    db.drop_collection(StoreDatabase.Collections.UsersCollection)

    # Create items collection with specified schema and unique index
    db.create_collection(
        StoreDatabase.Collections.ItemsCollection,
        validators[StoreDatabase.Collections.ItemsCollection],
    )
    db.set_collection(StoreDatabase.Collections.ItemsCollection)
    # db.collection.create_index({"name": 1}, unique=True)

    # Create users collection with specified schema and unique indices
    db.create_collection(
        StoreDatabase.Collections.UsersCollection,
        validators[StoreDatabase.Collections.UsersCollection],
    )
    db.set_collection(StoreDatabase.Collections.UsersCollection)
    db.collection.create_index({"username": 1}, unique=True)
    db.collection.create_index({"email": 1}, unique=True)

    with open(users_file, "r") as file:
        users: list[dict] = json.load(file)

        # Has each password, then insert each user
        for user in users:
            encoded_str: bytes = user["password"].encode()
            hashed_password: str = sha256(encoded_str).hexdigest()
            user["password"] = hashed_password

            db.insert_one(user)

    for file in json_files:
        parts = file.split("/")
        tag = parts[-1][:-5].replace("-", " ").title()

        with open(file) as f:
            json_data: dict = json.load(f)

            db.set_collection(StoreDatabase.Collections.ItemsCollection)
            for id, item in json_data.items():
                item.pop("id")
                item["category"] = StoreDatabase.Categories.GroceryNGourmetFood
                item["tags"] = [tag, "Candy", "Sweets"]
                # Avoid inserting duplicates
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
        "port": 27017,
        "host": "localhost",
    }

    load_database(**kwargs)
