import requests

BASE_URL = "https://sharmaji.pythonanywhere.com"


def test_home():
    response = requests.get(BASE_URL + "/")

    print("\nHOME TEST")
    print("Status:", response.status_code)
    print("Response:", response.text)


def test_register():
    response = requests.post(
        BASE_URL + "/register",
        json={
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
    )

    print("\nREGISTER TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())


def test_login():
    response = requests.post(
        BASE_URL + "/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    print("\nLOGIN TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())


if __name__ == "__main__":
    test_home()
    test_register()
    test_login()