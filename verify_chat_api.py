import requests
import sys
import json

BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/auth"
CHAT_URL = f"{BASE_URL}/chat"

EMAIL = "director@college.edu"
PASSWORD = "password"

def run_test():
    print("=== STARTING SWAGGER/API VERIFICATION ===")
    
    # 1. Login
    print(f"[-] Logging in as {EMAIL}...")
    res = requests.post(f"{AUTH_URL}/login", json={"email": EMAIL, "password": PASSWORD})
    if res.status_code != 200:
        print(f"[ERROR] Login failed: {res.text}")
        sys.exit(1)
    
    token = res.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Login Successful")

    # 2. Get Rooms
    print("[-] Fetching Chat Rooms...")
    res = requests.get(CHAT_URL, headers=headers)
    if res.status_code != 200:
        print(f"[ERROR] Get Rooms failed: {res.text}")
        sys.exit(1)
    
    rooms = res.json()
    print(f"[PASS] Fetched {len(rooms)} rooms")
    
    room_id = None
    if rooms:
        room_id = rooms[0]['id']
        print(f"[-] Using existing Room ID: {room_id}")
    else:
        print("[-] Creating new Room...")
        res = requests.post(f"{CHAT_URL}/create", json={"name": "Swagger Test Room", "type": "GROUP"}, headers=headers)
        if res.status_code != 201:
             print(f"[ERROR] Create Room failed: {res.text}")
             sys.exit(1)
        room_id = res.json()['room']['id']
        print(f"[PASS] Created Room ID: {room_id}")

    # 3. Send Message (The previously broken step)
    print(f"[-] Sending Message to Room {room_id}...")
    msg_content = "Swagger Verification Message"
    res = requests.post(f"{CHAT_URL}/message", json={"room_id": room_id, "content": msg_content}, headers=headers)
    
    if res.status_code == 200:
        print(f"[PASS] Message Sent! Response: {res.json()}")
    else:
        print(f"[ERROR] Send Message FAILED: {res.status_code} - {res.text}")
        sys.exit(1)

    # 4. Verify Persistence
    print(f"[-] Verifying Persistence (Get Messages)...")
    res = requests.get(f"{CHAT_URL}/messages/{room_id}", headers=headers)
    messages = res.json()
    
    found = False
    for m in messages:
        if m['content'] == msg_content:
            found = True
            if 'Sender' in m and m['Sender']['name']:
                print(f"[PASS] Message Found in DB with Sender Info: {m['Sender']['name']}")
            else:
                print(f"[WARN] Message Found but MISSING Sender Info: {m}")
            break
            
    if found:
        print("=== VERIFICATION SUCCESSFUL ===")
    else:
        print("[FAIL] Message NOT found in history!")

if __name__ == "__main__":
    run_test()
