import requests

BASE_URL = "http://localhost:8000/auth"
EMAIL = "director@college.edu"

print(f"[-] Requesting OTP for {EMAIL}...")
res = requests.post(f"{BASE_URL}/forgot-password", json={"email": EMAIL})
print(f"[*] Response: {res.text}")
