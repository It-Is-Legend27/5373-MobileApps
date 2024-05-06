"""Provides classes for validation of data.

Provides Item class an User class for validation of request body data.
"""

from pydantic import BaseModel, Field


class Item(BaseModel):
    """
    Provides JSON-schema for a "item" object / entry.
    """

    name: str = Field(description="The name of a item.")
    prod_url: str = Field(description="The product url of a item.")
    img_url: str = Field(description="The image url of a item.")
    price: float = Field(description="The price of a item.", ge=0)
    desc: str = Field(description="The description of a item.")
    category: str = Field(description="The category name of a item.")
    tags: list[str] = Field(description="A list of tags.")


class User(BaseModel):
    """
    Provides JSON-schema for a "user" object / entry.
    """

    first_name: str = Field(description="The first name of a user.")
    last_name: str = Field(description="The last name of a user.")
    username: str = Field(description="The username of a user.")
    email: str = Field(description="The email of a user.")
    password: str = Field(description="The password of a user.")

class Location(BaseModel):
    """
    Provides JSON-schema for a "location" object / entry.
    """

    username: str = Field(description="The username of a user.")
    latitude: float = Field(description="The latitude of the user.")
    longitude: float = Field(description="The longitude of the user.")
    timestamp: int = Field(
        description="The UNIX timestamp in milliseconds when the location was received."
    )

class FileBody(BaseModel):
    """
    Provides a JSON-schema for a "file" object containing base64 data of a file.
    """
    base64_content:str = Field(description="The base64 data of the file.")
    file_type:str = Field(description="The file type of the file.")
    file_name:str = Field(description="The name of the file.")