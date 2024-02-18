from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.results import (
    InsertOneResult,
    InsertManyResult,
    DeleteResult,
    UpdateResult,
    BulkWriteResult,
    UpdateResult,
)
from pymongo.errors import PyMongoError, ConnectionFailure, InvalidOperation
from rich import print
from rich.console import Console
from rich.traceback import install
import re
import sys
from bson.objectid import ObjectId
from bson.errors import InvalidId
from bson.son import SON


class MongoManager:
    def __init__(
        self,
        username: str = None,
        password: str = None,
        host: str = "localhost",
        port: int = 27017,
        database: str = None,
        collection: str = None,
    ) -> None:
        self.username: str = username
        self.password: str = password
        self.host: str = host
        self.port: int = port
        self.database: Database = None
        self.collection: Collection = None
        self.connection_url: str = None
        self.client: MongoClient = None

        if self.username is None and self.password is None:
            self.connection_url = f"mongodb://{self.host}:{self.port}/"
        else:
            # Need to check that a db name was passed in
            # Create the connection URL
            self.connection_url = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?authSource=admin"

        try:
            self.client = MongoClient(self.connection_url)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command("ismaster")
        except ConnectionFailure as e:
            print(f"Error: {e}")

        # if a db is specified then make connection
        if database is not None:
            self.setDb(database)

            # if db is specified then check for collection as well
            if collection is not None:
                self.collection = self.database[collection]

    def __str__(self):
        return self.database.name

    def setDb(self, database: str):
        """Sets the current database."""
        self.database = self.client[database]

    def setCollection(self, collection: str):
        """Sets the current collection."""
        self.collection = self.database[collection]

    def dropCollection(self, collection: str):
        self.database.drop_collection(collection)

    def dropDb(self, database: str):
        """Deletes a database."""
        self.client.drop_database(database)

    def get(
        self,
        query: dict = {},
        filter: dict = {"_id": 0},
        skip: int = 0,
        limit: int = 0,
        sort: list[tuple] = [("id", 1)],
    ) -> list[dict]:
        """
        Retrieves documents from the collection based on the provided criteria.

        :param query: Dictionary for filtering documents using MongoDB query syntax.
        :param skip: Integer specifying the number of documents to skip.
        :param limit: Integer specifying the maximum number of documents to return.
        :param sort_criteria: List of tuples specifying field and direction to sort by.
        :return: Dictionary with the operation's success status, result size, and data.
        """

        results: Cursor = (
            self.collection.find(query, filter).sort(sort).skip(skip).limit(limit)
        )
        return list(results)

    def post(self, document: list[dict] | dict) -> dict:
        if isinstance(document, dict):
            result: InsertOneResult = self.collection.insert_one(document)
            return {
                "acknowledged": result.acknowledged,
                "inserted_ids": [str(result.inserted_id)],
            }
        elif isinstance(document, list):
            results: InsertManyResult = self.collection.insert_many(document)

            results.inserted_ids = [str(objId) for objId in results.inserted_ids]
            return {
                "acknowledged": results.acknowledged,
                "inserted_ids": str(results.inserted_ids),
            }
        else:
            raise PyMongoError(message="Invalid document")

    def put(self, id_key: str, id_val: str, update_key: str, update_value: str) -> dict:
        """
        Updates the price of a specific item in the collection.

        :param item_id: The unique identifier for the item.
        :param new_price: The new price to set.
        :return: Result of the update operation.
        """
        if id_key == "_id" and MongoManager.is_valid_object_id(id_val):
            # Convert string ID to ObjectId
            id_val = ObjectId(id_val)

        # Perform the update
        result: UpdateResult = self.collection.update_one(
            {id_key: id_val},  # Query to match the document
            {"$set": {update_key: update_value}},  # Update operation
        )

        return {
            "acknowledged": result.acknowledged,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "raw_result": result.raw_result,
            "upserted_id": str(result.upserted_id),
        }

    def delete(self, query: dict) -> dict:
        result: DeleteResult = self.collection.delete_many(query)
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count,
            "raw_result": result.raw_result,
        }

    def close(self) -> None:
        self.client.close()

    def is_valid_object_id(id_str: str) -> bool:
        return ObjectId.is_valid(id_str)


if __name__ == "__main__":

    # info = {
    #     "username": "mongomin",
    #     "password": "horsedonkeyblanketbattery",
    #     "host": "localhost",
    #     "port": "27017",
    #     "db_name": "candy_store",
    #     "collection_name": "candies",
    # }

    query = sys.argv[1]

    mm = MongoManager()

    mm.setDb("candy_store")

    if query == "1":
        # Get all categories sorted ascending by name
        mm.setCollection("categories")

        categories = mm.get(sort_criteria=[("name", -1)], filter={"_id": 0, "count": 1})

        print(categories)
    elif query == "2":
        # Get candies sorted ascending by category and desc by price and filter to only see price, category, and name
        mm.setCollection("candies")

        candies = mm.get(
            sort_criteria=[("category", 1), ("price", -1)],
            filter={"_id": 0, "price": 1, "category": 1},
        )

        print(candies)
    elif query == "3":
        mm.setCollection("candies")
        regex_query = {
            "name": {"$regex": "crows", "$options": "i"}
        }  # '$options': 'i' makes it case-insensitive

        sourCandies = mm.get(
            query=regex_query,
            # filter={"_id":0,"name":1},
            sort_criteria=[("name", 1)],
        )
        print(sourCandies)
        print(len(sourCandies["data"]))

    elif query == "4":
        mm.setCollection("candies")
        sourCandies = mm.get(
            query={"category_id": 12},
            filter={"_id": 0, "price": 1, "category_id": 1, "name": 1},
        )
        print(sourCandies)
        print(len(sourCandies["data"]))

    elif query == "5":
        price_range_query = {"price": {"$gte": 100.00, "$lte": 150.00}}
        mm.setCollection("candies")
        rangeQuery = mm.get(
            query=price_range_query,
            filter={"_id": 0, "price": 1, "category_id": 1, "name": 1},
            sort_criteria={"price": -1},
        )
        print(rangeQuery)
        print(len(rangeQuery["data"]))
    elif query == "6":
        # original 49.99
        mm.setCollection("candies")
        print(mm.get(query={"id": "42688432308411"}))
    elif query == "7":
        # original 49.99
        mm.setCollection("candies")
        print(mm.put("id", "42688432308411", "price", 9.99))

    elif query == "8":
        # client = MongoClient()
        # db = client['candy_store']
        # collection = db['candies']

        # results = collection.find({'category_id':30},{'_id':0,"name":1,'price':1})
        # print(list(results))

        mm.setCollection("candies")
        for i in range(10):
            result = mm.get(
                sort_criteria=[("name", 1)],
                skip=(i * 3),
                limit=3,
                filter={"_id": 0, "name": 1},
            )
            print(result)
            print("=" * 30)
    elif query == "9":
        mm.setCollection("candies")
        result = mm.get(sort_criteria=[("name", 1)], filter={"_id": 0, "name": 1})
        print(result)
    elif query == "10":
        mm.setCollection("categories")
        doc = {
            "count": 23,
            "name": "Dirt Candy",
            "tast": "awesome",
            "color": "pink",
            "price": 99999.99,
        }
        mm.post(doc)
