## A06 - Location

### Angel Badillo, Miklos Moreno

### Description:

This API provides routes for querying a MongoDB for Awesome store records. These routes facilitate various functionalities including retrieving all item records, getting items by category, searching by keyword in name or description, filtering by price range, getting item details by ID,  getting images of each items by ID, updating prices and other attributes, as well as deleting items from the database. There are also routes for retrieving and posting location data for users, login and register of users, image upload, and more. In addition to the API, there is a React Native app,
Awesome Store App, which interacts with the API, as well as performs other functions such as allowing the user to search for items by category and name, view other users on Google Maps, uploaded images to the https://thehonoredone.live server, and chat with other users.

### App
[Awesome Store App](https://github.com/It-Is-Legend27/4443-5373-A05)

### Files

| # | File                                | Description                                                |
| :-: | ----------------------------------- | -------------------------------------------------------  |
| 1 | [api.py](./api.py)                     | Awesome Store API made with FastAPI.                    |
| 2 | [loadMongo.py](./loadMongo.py)         | Script for loading JSON data into database.             |
| 3 | [store_database.py](store_database.py)      | Wrapper class for CRUD operations on the database.   |
| 4 | [categoryJson](./categoryJson)        | Contains JSON files with candy information.             |
| 5 | [requirements.txt](./requirements.txt) | Lists all the required packages needed for the project. |
| 6 | [static/assets](./static/assets)                    | Contains static files used in the API.                  |
| 7 | [addData.py](./addData.py) | Script for loading JSON data into database. |
| 8 | [collection_validators.json](./collection_validators.json) | JSON file for validators / schema for collections. |
| 9 | [locations.json](./locations.json) | JSON file with user locations. |
| 10 | [models.py](./models.py) | Contains derived classes of BaseModel for response data. |
| 11 | [movies.json](./movies.json) | JSON file with generated movie information. |
| 12 | [user.json](./users.json) | JSON file with generated user information. |

### Instructions

#### Awesome Store API
- First, login to the server via SSH.
- Next, change the directory like so:

```
  cd /root/5373-MobileApps/Assignments/A05
```

- Start the virtual environment:

```
source .venv/bin/activate
```

- Run the script:

```
python api.py
```

- Go to https://thehonoredone.live:8085

#### Awesome Store React Native App
- First, ensure all required packages are installed with some package manager, for example:

```
yarn install
```

- Next, run the app with:
```
yarn expo start
```