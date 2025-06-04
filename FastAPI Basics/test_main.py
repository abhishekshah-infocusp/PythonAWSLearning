import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post("/items/", json={"name": "Test Item", "price": "123", "is_offer": True})
    assert response.status_code == 200
    assert response.json() == {"name": "Test Item", "price": 123.0, "is_offer": True}  

def test_read_item_by_id():
    response = client.get("/items/1", )

@pytest.mark.asyncio
async def test_read_item_all_inputs(async_test_client):
    item_id = 5

    request_body = {
        "q": "SampleQuery",
        "size": 42,
        "tags": ["Abhishek", "Deep"]
    }

    response = await async_test_client.post(f"/items/{item_id}", json=request_body)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["item_id"] == item_id
    assert json_data["q"] == "SampleQuery"
    assert json_data["size"] == 42
    assert json_data["tags"] == ["Abhishek", "Deep"]

@pytest.mark.asyncio
async def test_read_item_invalid_short_tag(async_test_client):
    item_id = 10
    request_body = {
        "q": "SampleQuery",
        "size": 10,
        "tags": ["A"]
    }
    response = await async_test_client.post(f"/items/{item_id}", json=request_body)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("Tag must be at least 2 characters long" in err.get("msg", "") for err in data["detail"])

