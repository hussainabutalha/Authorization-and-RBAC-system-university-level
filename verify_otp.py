import requests
import sys

BASE_URL = "http://localhost:8000/auth"
EMAIL = "director@college.edu"

def verify(otp):
    print(f"\n[-] Verifying OTP: {otp}...")
    try:
        res = requests.post(f"{BASE_URL}/verify-otp", json={"email": EMAIL, "otp": otp})
        print(f"[*] Verify Status: {res.status_code}")
        print(f"[*] Verify Body: {res.text}")
        
        if res.status_code == 200:
            print("[+] Verified!")
            
            print("\n[-] Resetting Password...")
            res = requests.post(f"{BASE_URL}/reset-password", json={
                "email": EMAIL, 
                "otp": otp, 
                "newPassword": "FinalNewPasword123!"
            })
            print(f"[*] Reset Status: {res.status_code}")
            print(f"[*] Reset Body: {res.text}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify(sys.argv[1])
    else:
        print("Usage: python verify_otp.py <OTP>")
