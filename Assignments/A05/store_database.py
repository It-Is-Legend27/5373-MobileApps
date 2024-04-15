"""Provides easy-to-use class for database operations.

Provides the class StoreDatabase to make it easier to perform database
operations on the online store database.
"""

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
    """Performs operations on database.

    Performs operations on MongoDB database.
    """

    class Categories(StrEnum):
        """Enums for representing categories.

        Represents categories.
        """

        Electronics: str = "Electronics"
        ClothingNAccessories = "Clothing & Accessories"
        HomeNKitchen = "Home & Kitchen"
        BooksNAudible = "Books & Audible"
        HealthNPersonalCare = "Health & Personal Care"
        ToysNGames = "Toys & Games"
        SportsNOutDoors = "Sports & Outdoors"
        Automotive = "Automotive"
        ToolsNHomeImprovement = "Tools & Home Improvement"
        GroceryNGourmetFood = "Grocery & Gourmet Food"
        PetSupplies = "Pet Supplies"
        OfficeProducts = "Office Products"
        Baby = "Baby"
        MusicalInstruments = "Musical Instruments"
        IndustrialNScientific = "Industrial & Scientific"
        MoviesNTV = "Movies & TV"
        PatioNLawnNGarden = "Patio, Lawn & Garden"
        ArtsNCraftsNSewing = "Arts, Crafts & Sewing"
        Miscellaneous = "Miscellaneous"

    class Collections(StrEnum):
        """Enums for representing collections.

        Represents the types of collections in the database.
        """

        ItemsCollection: str = "items"
        UsersCollection: str = "users"
        LocationsCollection: str = "locations"

    def __init__(
        self,
        username: str = None,
        password: str = None,
        host: str = "localhost",
        port: int = 27017,
        database: str = None,
        collection: str = None,
    ) -> None:
        """ "Connects to the database.
        Establishes a connection to the database.
        """
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

    def set_database(self, database: str) -> None:
        """Sets the current database."""
        self.database = self.client[database]

    def create_collection(self, collection: str | Collections, validator: dict = None):
        """Creates a new collection.

        Creates a new collection

        Args:
            collection (str, StoreDatabase.Collections): Name of the collection.
            validator (dict, optional): Validator for jsonSchema of the documents in the collection.
        """
        self.database.create_collection(str(collection), validator=validator)

    def set_collection(self, collection: str | Collections):
        """Sets the collection.

        Sets the collection.

        Args:
            collection (str, StoreDatabase.Collections): Name of collection.
        """
        self.collection = self.database[str(collection)]

    def drop_collection(self, collection: str | Collections):
        """Drops a collection.

        Drops a collection from the database.

        Args:
            collection (str, StoreDatabase.Collections): Name of the collection.
        """
        self.database.drop_collection(str(collection))

    def drop_database(self, database: str):
        """Drops a database.

        Drops the specified database.

        Args:
            datbase (str): Name of the database.
        """
        self.client.drop_database(database)

    def distinct(self, key: str, filter: dict = {}) -> list[str]:
        """Returns distinct values in a collection.

        Returns distinct values in a collecion.

        Args:
            key (str): The key / field name to inspect.
            filter (dict, optional): Other filters to apply.
        Returns:
            A list of distinct values for a given key.
        """
        distinct_vals: list[str] = self.collection.distinct(key, filter)

        return distinct_vals

    def find_one(self, filter: dict = {}, projection: dict = {}) -> dict | None:
        """Return one matching document.

        Returns one matching document for a given query.

        Args:
            filter (dict): Filter for query.
            projection (dict, optional): Specifies what fields to include, exclude, etc.
        Returns:
            A dict for the matching document.
        """
        result: dict = None
        result = self.collection.find_one(filter, projection)

        if result:
            for key, value in result.items():
                if isinstance(value, ObjectId):
                    result.update({key: str(value)})
        return result

    def find(
        self,
        filter: dict = {},
        projection: dict = {},
        skip: int = 0,
        limit: int = 0,
        sort: list[tuple] = [("_id", 1)],
    ) -> list[dict]:
        """Returns matching documents.

        Retrieves documents from the collection based on the provided criteria.

        Args:
            filter (dict, optional): Filter for the query.
            projection (dict, optional): Project for the results.
            skip (int, optional): Number of documents to skip.
            limit (int, optional): Number of documents to return. Limit of 0 returns all matches.
            sort (list[tuple], optional): Criteria for sorting documents.
        Returns:
            List of matching documents.
        """

        results: Cursor = (
            self.collection.find(filter, projection).sort(sort).skip(skip).limit(limit)
        )

        result_list: list[dict] = []
        for doc in results:
            fdoc: dict = dict(doc)
            for key, value in fdoc.items():
                if isinstance(value, ObjectId):
                    fdoc.update({key: str(value)})
            result_list.append(fdoc)
        return result_list

    def insert_one(self, document: dict) -> dict:
        """Inserts a document.

        Inserts a document into the collection.

        Args:
            document (dict): Document to be inserted.
        Returns:
            Dict describing the result of the operation.
        """
        result: InsertOneResult = self.collection.insert_one(document)
        return {
            "acknowledged": result.acknowledged,
            "inserted_id": str(result.inserted_id),
        }

    def insert_many(self, documents: list[dict]) -> dict:
        """Insert multiple documents.

        Inserts a list or tuple of documents into the collection.

        Args:
            documents (list[dict]): Documents to be inserted.
        Returns:
            Dict describing the result of the operation.
        """
        result: InsertManyResult = self.collection.insert_many(
            documents=documents, ordered=False
        )
        return {
            "acknowledged": result.acknowledged,
            "inserted_ids": [str(objId) for objId in result.inserted_ids],
        }

    def update_one(self, filter: dict, update: dict, upsert: bool = False) -> dict:
        """Updates one matching documents.

        Updates one matching document based of filter and update dict.

        Args:
            filter (dict): Filter for the query.
            update (dict): New values for the document.
            upsert (bool, optional): If True, inserts new document, if not existing. Default is False.
        Returns:
            Dict describing the result of the operation.
        """
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
        """Updates all matching documents.

        Updates all matching document based of filter and update dict.

        Args:
            filter (dict): Filter for the query.
            update (dict): New values for the document.
            upsert (bool, optional): If True, inserts new document, if not existing. Default is False.
        Returns:
            Dict describing the result of the operation.
        """
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
        """Deletes one matching document.

        Deletes one matching document based on filter.

        Args:
            filter (dict): Filter for the query.
        Returns:
            Dict describing the result of the operation.
        """
        result: DeleteResult = self.collection.delete_one(filter)
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count,
            "raw_result": result.raw_result,
        }

    def delete_many(self, filter: dict) -> dict:
        """Deletes all matching documents.

        Deletes all matching documents based on filter.

        Args:
            filter (dict): Filter for the query.
        Returns:
            Dict describing the result of the operation.
        """
        result: DeleteResult = self.collection.delete_many(filter)
        return {
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count,
            "raw_result": result.raw_result,
        }

    def close(self) -> None:
        """Close connection to database.

        Closes the connection to the database.
        """
        self.client.close()

    def is_valid_object_id(id_str: str) -> bool:
        """Checks if str is valid ObjectID.

        Checks if str is valid ObjectID.

        Returns:
            True if str is valid ObjectID, false otherwise.
        """
        return ObjectId.is_valid(id_str)

    def str_to_object_id(id_str: str) -> ObjectId:
        """Returns ObjectID for str.

        Converts a str into an ObjectID.

        Returns:
            ObjectID for the given str.
        """
        return ObjectId(id_str)
