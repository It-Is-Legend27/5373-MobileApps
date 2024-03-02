import requests

# Base URL of your FastAPI application
BASE_URL = "https://thehonoredone.live:8084"


def test_get_candies():
    response = requests.get(f"{BASE_URL}/candies?limit=5")
    print(f"GET /candies?limit=5: {response.json()}")
    assert response.status_code == 200
    print("GET /candies test passed.")


def test_get_categories():
    response = requests.get(f"{BASE_URL}/categories")
    print(f"GET /categories: {response.json()}")
    assert response.status_code == 200
    print("GET /categories test passed.")


def test_get_candies_by_category(category_id=0):
    response = requests.get(f"{BASE_URL}/candies?category_id={category_id}&limit=5")
    print(f"GET /candies?category_id={category_id}: {response.json()}")
    assert response.status_code == 200
    print("GET /candies?category_id=val test passed.")


def test_get_candies_by_keyword(keyword="sugar"):
    response = requests.get(f"{BASE_URL}/candies?desc={keyword}&limit=5")
    print(f"GET /candies?desc={keyword}: {response.json()}")
    assert response.status_code == 200
    print("GET /candies/?desc=val test passed.")


def test_get_candies_by_name(name="mars"):
    response = requests.get(f"{BASE_URL}/candies?name={name}&limit=5")
    print(f"GET /candies?name={name}&?limit=5: {response.json()}")
    assert response.status_code == 200
    print("GET /candies?name=val test passed.")


def test_get_candies_by_price_range(low=1.0, high=30.0):
    response = requests.get(f"{BASE_URL}/candies?min_price={low}&max_price={high}&limit=5")
    print(f"GET /candies?min_price={low}&max_price={high}: {response.json()}")
    assert response.status_code == 200
    print(f"GET /candies?min_price=val&max_price=val test passed.")


def test_get_candy_by_id(id=0):
    response = requests.get(f"{BASE_URL}/candies/id/{id}")
    print(f"GET /candies/id/{id}: {response.json()}")
    assert response.status_code == 200
    print("GET /candies/id/ test passed.")


def test_get_candy_image(id=42688339869883):
    response = requests.get(f"{BASE_URL}/candies/id/{id}/image")
    print(f"GET /candies/id/{id}/image: {response.headers}")
    assert response.status_code == 200
    print("GET /candies/id/{id}/image test passed.")


def test_update_candy(id=0, name="Test"):
    body = {"id": id, "name": name}
    response = requests.put(f"{BASE_URL}/candies", json=body)
    print(f"PUT /candies body={body}: {response.json()}")
    assert response.status_code == 200
    print("PUT /candies test passed.")


def test_add_new_candy():
    new_candy = {
        "id": 0,
        "name": "Test",
        "desc": "Test",
        "prod_url": "Hi",
        "image_url": "Hi",
        "price": 0.00,
        "category": "Fortnite",
        "category_id": 100,
    }
    response = requests.post(f"{BASE_URL}/candies", json=new_candy)
    print(f"POST /candies body={new_candy}: {response.json()}")
    assert response.status_code == 200
    print("POST /candies test passed.")


def test_delete_candy(id=0):
    response = requests.delete(f"{BASE_URL}/candies/id/{id}")
    print(f"DELETE /candies/id/{id}: {response.json()}")
    print(response.json())
    assert response.status_code == 200
    print(f"DELETE /candies/id/ test passed.")


def run_tests():
    test_get_candies()
    test_get_categories()
    test_get_candies_by_category()
    test_get_candies_by_keyword()
    test_get_candies_by_name()
    test_get_candies_by_price_range()
    test_get_candy_by_id()
    test_get_candy_image()
    test_delete_candy()
    test_add_new_candy()
    test_update_candy()


if __name__ == "__main__":
    from rich import print
    run_tests()
