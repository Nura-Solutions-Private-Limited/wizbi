import json


# def test_create_group(client):
#     data = {"name": "testgroup","description": "test@example.com"}
#     response = client.post("/rebiz/v1/group", data=json.dumps(data))
#     assert response.status_code == 200

def test_create_user(client):
    data = {"username": "testuser123",
            "email": "testuser@nofoobar.com",
            "password": "testing",
            "type": "admin"}

    response = client.post("/rebiz/v1/register", data=json.dumps(data))
    print(response)
    assert response.status_code == 200
    # assert response.json()["email"] == "testuser@nofoobar.com"
    # assert response.json()["is_active"] == True
