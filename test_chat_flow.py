import socketio
import requests
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/chat"
AUTH_URL = f"{BASE_URL}/auth"

# Test User Credentials
EMAIL = "director@college.edu"
PASSWORD = "password" # Assuming default or known password. If unknown, we might need a known user.
# Wait, user said "password is 'password'" in history, so likely valid.

sio = socketio.Client()
received_messages = []

def login():
    print(f"[-] Logging in as {EMAIL}...")
    res = requests.post(f"{AUTH_URL}/login", json={"email": EMAIL, "password": "password"})
    if res.status_code != 200:
        # Try Creating user if login fails? Or use a known user from DB seed?
        # Assuming DB has users from previous context.
        print(f"[!] Login failed: {res.text}")
        sys.exit(1)
    return res.json()['token']

@sio.event
def connect():
    print("[+] Socket Connected")

@sio.event
def newMessage(data):
    print(f"[+] Received 'newMessage' event: {data}")
    received_messages.append(data)

@sio.event
def disconnect():
    print("[-] Socket Disconnected")

def test_flow():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Connect Socket
    print("[-] Connecting to Socket.IO...")
    # Passing token in auth is optional depending on implementation (currently backend doesn't seem to enforce auth on socket connect, but logic logic might use it)
    # Backend socket_events.py connect handler doesn't check auth.
    sio.connect(BASE_URL)
    
    # 2. Get a Room (or create one)
    print("[-] Fetching rooms...")
    res = requests.get(API_URL, headers=headers)
    rooms = res.json()
    
    if not rooms:
        print("[-] No rooms found, creating one...")
        res = requests.post(f"{API_URL}/create", json={"name": "Test Room", "type": "GROUP"}, headers=headers)
        room_id = res.json()['room']['id']
    else:
        room_id = rooms[0]['id']
    
    print(f"[-] Using Room ID: {room_id}")

    # 3. Join Room
    print(f"[-] Joining Room {room_id}...")
    sio.emit('joinRoom', room_id)
    time.sleep(1) 

    # 4. Send Message via HTTP
    print("[-] Sending Message via HTTP POST...")
    content = f"Test Message {time.time()}"
    res = requests.post(f"{API_URL}/message", json={"room_id": room_id, "content": content}, headers=headers)
    print(f"[*] Send Status: {res.status_code}")
    
    # 5. Wait for events
    print("[-] Waiting for socket event...")
    start = time.time()
    while time.time() - start < 5:
        if received_messages:
            break
        time.sleep(0.1)

    if received_messages:
        print("[SUCCESS] Message received via socket!")
        # Validate data structure
        msg = received_messages[0]
        if 'Sender' in msg and 'name' in msg['Sender']:
            print("[SUCCESS] Message has Sender info ok")
        else:
            print("[FAIL] Message MISSING Sender info")
    else:
        print("[FAIL] No message received via socket.")

    sio.disconnect()

if __name__ == "__main__":
    test_flow()
