def test_login_customer(client):
    r = client.post(
        "/api/auth/login",
        json={"email": "customer@demo.com", "password": "demo1234"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["user"]["role"] == "customer"
