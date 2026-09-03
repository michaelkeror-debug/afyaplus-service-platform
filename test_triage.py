from fastapi.testclient import TestClient
from triage_model_call import app

client = TestClient(app)

def get_auth_headers(username: str, password: str) -> dict:
    login_response = client.post(
        "/token",
        json={
            "username": username,
            "password": password
        }
    )

    print("LOGIN STATUS:", login_response.status_code)
    print("LOGIN RESPONSE:", login_response.text)

    assert login_response.status_code == 200, (
        f"Login failed: {login_response.status_code} "
        f"{login_response.text}"
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_missing_authentication_returns_401():
    response = client.post(
        "/triage",
        json={
            "patient_message": "Child has fever",
            "county": "Nairobi"
        }
    )

    assert response.status_code == 401


def test_wrong_credentials_returns_401():
    response = client.post(
        "/token",
        json={
            "username": "wrong",
            "password": "wrong123"
        }
    )

    assert response.status_code == 401



def test_successful_login_returns_200():
    response = client.post(
        "/token",
        json={
            "username": "mercy",
            "password": "logistics2026"
        }
    )

    assert response.status_code == 200


def test_invalid_input_with_authentication_returns_422():
    headers = get_auth_headers(
        "mercy",
        "logistics2026"
    )

    response = client.post(
        "/triage",
        headers=headers,
        json={
            "patient_message": "Hi",
            "county": "Nairobi"
        }
    )

    assert response.status_code == 422



def test_valid_authentication_wrong_authorization_returns_403():
    headers = get_auth_headers(
        "james",
        "newpassword"
    )

    response = client.post(
        "/triage",
        headers=headers,
        json={
            "patient_message": "Child has fever",
            "county": "Nairobi"
        }
    )

    assert response.status_code == 403

def test_valid_authentication_and_valid_authorization_returns_200():
    headers = get_auth_headers(
        "mercy",
        "logistics2026"
    )

    response = client.post(
        "/triage",
        headers=headers,
        json={
            "patient_message": "Child has fever",
            "county": "Nairobi"
        }
    )

    assert response.status_code == 200
