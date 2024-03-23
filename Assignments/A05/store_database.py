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
)
from pymongo.errors import PyMongoError, ConnectionFailure, InvalidOperation
from rich import print
from bson.objectid import ObjectId
from bson.errors import InvalidId
from bson.son import SON
from enum import Enum, StrEnum


class StoreDatabase:
    class Collections(StrEnum):
        ItemsCollection: str = "items"
        CategoriesCollection: str = "categories"
        UsersCollection: str = "users"

    def __init__(
        self,
        username: str = None,
        password: str = None,
        host: str = "localhost",
        port: int = 27017,
        database: str = None,
        collection: str = None,
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.database: Database = None
        self.collection: Collection = None
        self.client: MongoClient = None
        connection_url: str = None

        if username is None or password is None:
            connection_url: str = f"mongodb://{self.host}:{self.port}/"
        else:
            # Need to check that a db name was passed in
            # Create the connection URL
            connection_url: str = (
                f"mongodb://{username}:{password}@{self.host}:{self.port}/{self.database}?authSource=admin"
            )
        try:
            self.client = MongoClient(connection_url)
            # The ismaster command is cheap and does not require auth.
            self.client["admin"].command("ismaster")
        except ConnectionFailure as e:
            print(f"Error: {e}")

        # if a db is specified then make connection
        if database is not None:
            self.set_database(database)

            # if db is specified then check for collection as well
            if collection is not None:
                self.set_collection(collection)

    def __repr__(self) -> str:
        return f"MongoManager(host= '{self.host}', port= {self.port})"

    def set_database(self, database: str) -> None:
        """Sets the current database."""
        self.database = self.client[database]

    def create_collection(self, collection: str | Collections, validator: dict):
        self.database.create_collection(str(collection), validator=validator)

    def set_collection(self, collection: str | Collections):
        """Sets the current collection."""
        self.collection = self.database[str(collection)]

    def drop_collection(self, collection: str | Collections):
        self.database.drop_collection(str(collection))

    def drop_database(self, database: str):
        """Deletes a database."""
        self.client.drop_database(database)

    def find(
        self,
        query: dict = {},
        filter: dict = {},
        skip: int = 0,
        limit: int = 0,
        sort: list[tuple] = [("_id", 1)],
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

    def insert_one(self, document: dict) -> dict:
        result: InsertOneResult = self.collection.insert_one(document)
        return {
            "acknowledged": result.acknowledged,
            "inserted_id": str(result.inserted_id),
        }

    def insert_many(self, documents: list[dict]) -> dict:
        result: InsertManyResult = self.collection.insert_many(
            documents=documents, ordered=False
        )
        return {
            "acknowledged": result.acknowledged,
            "inserted_ids": [str(objId) for objId in result.inserted_ids],
        }

    def update_one(self, filter: dict, update: dict, upsert: bool = False) -> dict:
        """
        Updates the price of a specific item in the collection.

        :param item_id: The unique identifier for the item.
        :param new_price: The new price to set.
        :return: Result of the update operation.
        """

        # if "_id" in update.keys() and StoreDB.is_valid_object_id(update["_id"]):
        #     update["_id"] = ObjectId(update["_id"])

        # Perform the update
        result: UpdateResult = self.collection.update_one(
            filter,  # Query to match the document
            update,  # Update operation
        )

        return {
            "acknowledged": result.acknowledged,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "raw_result": result.raw_result,
            "upserted_id": str(result.upserted_id),
        }

    def update_many(self, filter: dict, update: dict, upsert: bool = False) -> dict:
        result: UpdateResult = self.collection.update_many(
            filter,
            update,
            upsert,
        )

        return {
            "acknowledged": result.acknowledged,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "raw_result": result.raw_result,
            "upserted_id": str(result.upserted_id),
        }

    def delete_one(self, filter: dict) -> dict:
        result: DeleteResult = self.collection.delete_one(filter)
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count,
            "raw_result": result.raw_result,
        }

    def delete_many(self, filter: dict) -> dict:
        result: DeleteResult = self.collection.delete_many(filter)
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count,
            "raw_result": result.raw_result,
        }

    def close(self) -> None:
        self.client.close()

    def is_valid_object_id(id_str: str) -> bool:
        return ObjectId.is_valid(id_str)

    def str_to_object_id(id_str: str) -> ObjectId:
        return ObjectId(id_str)
