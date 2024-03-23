"""Provides classes for validation of data.

Provides Item class an User class for validation of request body data.
"""

from pydantic import BaseModel, Field


class Item(BaseModel):
    """
    Provides JSON-schema for a "item" object / entry.
    """

    # id: str = Field(description="The ID of a item.")
    name: str = Field(description="The name of a item.")
    prod_url: str = Field(description="The product url of a item.")
    img_url: str = Field(description="The image url of a item.")
    price: float = Field(description="The price of a item.", ge=0)
    desc: str = Field(description="The description of a item.")
    category: str = Field(description="The category name of a item.")


class User(BaseModel):
    """
    Provides JSON-schema for a "user" object / entry.
    """

    # id: str = Field(description="The ID of a user.")
    first_name: str = Field(description="The first name of a user.")
    last_name: str = Field(description="The last name of a user.")
    username: str = Field(description="The username of a user.")
    email: str = Field(description="The email of a user.")
    password: str = Field(description="The password of a user.")
