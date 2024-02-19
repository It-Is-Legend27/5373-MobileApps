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
            self.setDb(database)

            # if db is specified then check for collection as well
            if collection is not None:
                self.collection = self.database[collection]

    def __repr__(self) -> str:
        return f"MongoManager(host= '{self.host}', port= {self.port})"

    def setDb(self, database: str) -> None:
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
