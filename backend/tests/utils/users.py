from db.views.users import create_new_user, get_user_by_username
# from db.repository.users import get_user_by_email
from fastapi.testclient import TestClient
from schemas.users import UserCreate
from sqlalchemy.orm import Session


def user_authentication_headers(client: TestClient, username: str, password: str):
    data = {"username": username, "password": password}
    r = client.post("/login/token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def authentication_token_from_email(client: TestClient, username: str, db: Session):
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = "random-passW0rd"
    email = "testmail@test.com"
    user = get_user_by_username(username=username, db=db)
    if not user:
        user_in_create = UserCreate(username=username, email=email, password=password)
        user = create_new_user(user=user_in_create, db=db)
    return user_authentication_headers(client=client, email=email, password=password)
