from store_database import StoreDatabase
import json
from rich import print

db = StoreDatabase("angel", "aB_1618401m", database="awesome_store", collection="items")

with open("movies.json", "r") as file:
    data = json.load(file)

    for item in data:
        # item["price"] = float(item["price"]) - 0.01
        item["img_url"] = "https://th.bing.com/th/id/R.be01e1d41ec8cd1094dcc578aa7ac45e?rik=OlvQBPFagFJPHw&pid=ImgRaw&r=0"

    with open("movies.json", "w") as file:
        json.dump(data, file)
    
    db.insert_many(data)