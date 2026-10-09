def _login(client):
    r = client.post(
        "/api/auth/login",
        json={"email": "customer@demo.com", "password": "demo1234"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_mock_pay_success_marks_order_paid_and_decrements_stock(client):
    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}
    products = client.get("/api/products").json()
    pid = products[0]["id"]
    stock_before = products[0]["stock"]
    client.post("/api/cart/items", headers=headers, json={"product_id": pid, "quantity": 1})
    order = client.post(
        "/api/orders",
        headers=headers,
        json={
            "shipping_name": "Demo",
            "shipping_phone": "10086",
            "shipping_address": "Jakarta",
        },
    ).json()
    pay = client.post(
        "/api/payments/mock", headers=headers, json={"order_id": order["id"]}
    ).json()
    conf = client.post(
        f"/api/payments/mock/{pay['id']}/confirm",
        headers=headers,
        json={"result": "succeeded"},
    )
    assert conf.status_code == 200, conf.text
    assert conf.json()["order"]["status"] == "paid"
    assert conf.json()["payment"]["status"] == "succeeded"
    after = client.get(f"/api/products/{pid}").json()
    assert after["stock"] == stock_before - 1


def test_mock_pay_fail_cancels_order(client):
    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}
    pid = client.get("/api/products").json()[0]["id"]
    client.post("/api/cart/items", headers=headers, json={"product_id": pid, "quantity": 1})
    order = client.post(
        "/api/orders",
        headers=headers,
        json={
            "shipping_name": "Demo",
            "shipping_phone": "10086",
            "shipping_address": "Jakarta",
        },
    ).json()
    pay = client.post(
        "/api/payments/mock", headers=headers, json={"order_id": order["id"]}
    ).json()
    conf = client.post(
        f"/api/payments/mock/{pay['id']}/confirm",
        headers=headers,
        json={"result": "failed"},
    )
    assert conf.status_code == 200, conf.text
    assert conf.json()["order"]["status"] == "cancelled"
    assert conf.json()["payment"]["status"] == "failed"
