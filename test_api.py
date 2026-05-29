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
            "username": "maths",
            "password": "maths",
            "role": "staff"
        }
    )

    print("\nREGISTER TEST")
    print("Status:", response.status_code)  
    print("Response:", response.json())

def test_login():
    response = requests.post(
        BASE_URL + "/login",
        json={
            "username": "sandeep",
            "password": "sandeep"
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
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4MDA0Mzg4NywianRpIjoiOWFlMTJjNjMtOTIyMS00YTZkLTk4MmYtMTdiZDMxNjEwM2JlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InJhaHVsIiwibmJmIjoxNzgwMDQzODg3LCJjc3JmIjoiMDQ2MWE0NzktNzQ5NS00MDNhLThmODYtY2VmNzRkM2I3YTI2IiwiZXhwIjoxNzgwMDQ3NDg3LCJyb2xlIjoic3R1ZGVudCJ9.AfmNfXNzJw-ete-oJJbBuAoDhZLj1S1sFbCqKNsQmLU"
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

def test_add_staff_profile():
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4MDA0NTIyMywianRpIjoiOWM2MDMwN2ItNjMzNi00YWRiLWFlYmEtY2QxZjA3NTY1MTJkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzgwMDQ1MjIzLCJjc3JmIjoiYjg3ZjI2OWQtYWJkNi00ODc1LThjMmUtZWZhZTRlMDA4OTdhIiwiZXhwIjoxNzgwMDQ4ODIzLCJyb2xlIjoiYWRtaW4ifQ.sQ1Zo7F-8ZJWMt7L9cNdA7HuX1o2pnxIBDeOfLjIS38"
    response = requests.post(
        BASE_URL + "/register_staff",
        json={ 
            "username": "chem", 
            "password": "chem", 
            "first_name": "Dr Manuel", 
            "last_name": "Rodrigues", 
            "email": "manuel.rodrigues@nexgen.com", 
            "phone": "9876543210", 
            "department": "Chemistry", 
            "designation": "Head of Department" 
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )

    print("\nADD STAFF TEST")
    print("Status:", response.status_code)
    print("Response:", response.json())




if __name__ == "__main__":
    test_home()
    # test_register()
    # test_login()
    # test_delete_user()
    # test_add_batch()
    # test_get_batches()
    # test_register_student()
    # test_all()
    # test_profiles()
    # test_add_staff_profile()