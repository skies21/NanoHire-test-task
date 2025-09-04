from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_to_order():
    response = client.post("/add_to_order/", json={"order_id": 1, "product_id": 1, "quantity": 2})
    assert response.status_code == 200

    # Проверяем, что ответ соответствует любому из двух вариантов
    assert response.json()['message'] in ["Product added to order", "Product quantity updated"]
