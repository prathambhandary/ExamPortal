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
            "username": "rahul",
            "password": "rahul",
            "role": "student"
        }
    )

    print("\nREGISTER TEST")
    print("Status:", response.status_code)  
    print("Response:", response.json())


def test_login():
    response = requests.post(
        BASE_URL + "/login",
        json={
            "username": "Rahul",
            "password": "rahul"
        }
    )

    print("\nLOGIN TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())

def test_delete_user():
    response = requests.post(
        BASE_URL + "/delete_user",
        json={
            "username": "Rahul"
        }
    )

    print("\nDELETE USER TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_home()
    test_register()
    # test_login()
    # test_delete_user()