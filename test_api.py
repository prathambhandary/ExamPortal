import requests

BASE_URL = "https://sharmaji.pythonanywhere.com"
# BASE_URL = "http://127.0.0.1:7000"


def test_home():
    response = requests.get(BASE_URL + "/")

    print("\nHOME TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())


def test_register():
    response = requests.post(
        BASE_URL + "/register",
        json={
            "username": "admin",
            "password": "admin",
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
            "username": "rahul",
            "password": "rahul"
        }
    )

    print("\nLOGIN TEST")
    print("Status:", response.status_code)
    print("Response:", response.text)

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

def test_add_batch():
    response = requests.post(
        BASE_URL + "/add_batch",
        json={
            "batch_name": "JEE 2025",
            "course": "PCMC",
            "year": 2025
        }
    )

    print("\nADD BATCH TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())

def test_get_batches():
    response = requests.get(BASE_URL + "/get_batches")

    print("\nGET BATCHES TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())

def test_register_student():
    data = {
        "username": "ram",
        "password": "ram",
        "first_name": "Ram",
        "last_name": "Sharma",
        "roll_number": "CS005",
        "batch_name": "JEE2026",
        "email": "ram@example.com",
        "student_phone": "1452345678",
        "parent_phone":  "6548451211",
        "stream": "PCMC",
        "target_year": 2027,
        "gender": "Male",
        "current_role": "admin"
    }

    response = requests.post(
        BASE_URL+"/register_student",
        json=data
    )
    print("\nREGISTER STUDENT TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())

def test_all():
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3OTg5NzAzMywianRpIjoiNGI4N2NhYjItNjdmYi00YWNiLThmMmMtYmU2NWIxODZhMTQ4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzc5ODk3MDMzLCJjc3JmIjoiMjExOTg0Y2MtZjhlZS00ODlmLWJkNTYtMjc1Mjg0ZTU5MzM1IiwiZXhwIjoxNzc5OTAwNjMzLCJyb2xlIjoiYWRtaW4ifQ.Au7A25jXjPTgIDl0tgtVNmxBTxwGrl9srwHVkat8rxg"
    response = requests.post(
        BASE_URL + "/students/search",
        json={
            "first_name":"dheeraj"
            },
        headers={"Authorization": f"Bearer {access_token}"}
    )

    print("\nALL TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())

def test_profiles():
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3OTkwNjQ1OCwianRpIjoiNzE2MTVjMDgtMjdhNS00YjAxLWJjMDMtMGZlMTYxMGM1YTAyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzc5OTA2NDU4LCJjc3JmIjoiMTM3ZmE4MTgtNmQzMC00M2IzLWE2NzctZGYxNGIyNzg3YTI3IiwiZXhwIjoxNzc5OTEwMDU4LCJyb2xlIjoiYWRtaW4ifQ.kj4Bb82l1N2zdUt09ckZcJCO5Wm-RyWM2QGCx0Cr6j8"
    response = requests.post(
        BASE_URL + "/get_student_profile",
        json={
            "username":"rahul"
            },
        headers={"Authorization": f"Bearer {access_token}"}
    )

    print("\nPROFILE TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())
if __name__ == "__main__":
    test_home()
    # test_register()
    test_login()
    # test_delete_user()
    # test_add_batch()
    # test_get_batches()
    # test_register_student()
    # test_all()
    # test_profiles()