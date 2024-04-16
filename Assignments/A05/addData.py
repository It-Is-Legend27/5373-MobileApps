from store_database import StoreDatabase
import json
from rich import print

db = StoreDatabase("angel", "aB_1618401m", database="awesome_store", collection="items")

with open("MOCK_DATA.json", "r") as file:
    data = json.load(file)

    for item in data:
        item["price"] = float(item["price"])
        item["tags"] = [item["tags"], "Entertainment"]

    with open("movies.json", "w") as file:
        json.dump(data, file)