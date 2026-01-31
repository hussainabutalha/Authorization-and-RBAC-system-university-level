import requests
import sys

BASE_URL = "http://localhost:8000/auth/token-swagger"
EMAIL = "director@college.edu"
PASSWORD = "password"

def test_swagger_login():
    print(f"[-] Testing Swagger (Form Data) Login against {BASE_URL}...")
    
    # Swagger uses Form Data (application/x-www-form-urlencoded)
    # Requests `data` parameter sends form data.
    payload = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    res = requests.post(BASE_URL, data=payload)
    
    if res.status_code == 200:
        data = res.json()
        if "access_token" in data and data["token_type"] == "bearer":
            print("[PASS] Swagger Login Successful. Token received.")
            print(f"Token: {data['access_token'][:20]}...")
        else:
            print(f"[FAIL] Unexpected Response Format: {data}")
            sys.exit(1)
    else:
        print(f"[FAIL] Login Failed: {res.status_code} - {res.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_swagger_login()
