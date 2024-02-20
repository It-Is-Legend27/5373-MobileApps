## A04 - Candy Store

### Angel Badillo

### Description:

This API provides routes for querying a MongoDB for candy store records. These routes facilitate various functionalities including retrieving all candies, getting candies by category, searching by keyword in name or description, filtering by price range, getting candy details by ID,  getting images of each candy by ID, updating prices and other attributes, as well as deleting candies from the database.

### Files

| # | File                                | Description                                             |
| :-: | ----------------------------------- | ------------------------------------------------------- |
| 1 | [api.py](./api.py)                     | Candy Store API made with FastAPI.                      |
| 2 | [loadMongo.py](./loadMongo.py)         | Script for loading JSON data into database.             |
| 3 | [mongoManager.py](mongoManger.py)      | Wrapper class for CRUD operations on MongoDB.           |
| 4 | [/categoryJson](./categoryJson)        | Contains JSON files with candy information.             |
| 5 | [requirements.txt](./requirements.txt) | Lists all the required packages needed for the project. |
| 6 | [/static](./static)                    | Contains static files used in the API.                  |

### Instructions

- First, login to the server via SSH.
- Next, change the directory like so:
```
  cd /root/A04
  ```
- Start the virtual environment:
```
source .venv/bin/activate
```
- Run the script:
```
python api.py
```
- Go to https://thehonoredone.live:8084