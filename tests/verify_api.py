import requests
import json
import time

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "director@college.edu"
ADMIN_PASSWORD = "password"

# Global Storage
admin_token = None
student_token = None
student_id = None
classroom_id = None
room_id = None

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def check(response, expected_code=200, task_name="Task"):
    if response.status_code == expected_code:
        log(f"{task_name} PASSED ({response.status_code})", "SUCCESS")
        return True
    else:
        log(f"{task_name} FAILED. Expected {expected_code}, got {response.status_code}", "ERROR")
        try:
            log(f"Response: {response.json()}", "ERROR")
        except:
            log(f"Response: {response.text}", "ERROR")
        return False

def run_tests():
    global admin_token, student_token, student_id, classroom_id, room_id

    # 1. AUTHENTICATION
    log("=== TESTING AUTHENTICATION ===")
    
    # Login Admin
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if check(res, 200, "Login Admin"):
        data = res.json()
        admin_token = data['token']
        log(f"Admin Token: {admin_token[:10]}...")
    else:
        log("Cannot proceed without admin login.", "CRITICAL")
        return

    # Create Student User
    log("=== TESTING USER CREATION ===")
    new_student_email = f"student_{int(time.time())}@college.edu"
    res = requests.post(f"{BASE_URL}/auth/create-user", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Student", 
            "email": new_student_email, 
            "password": "password",
            "role": "Student",
            "sub_role": "None"
        }
    )
    if check(res, 201, "Create User (Student)"):
        student_id = res.json()['user']['id']
    else:
        log("Failed to create student. Testing with existing if possible or aborting.", "WARNING")

    # Login Student
    if student_id:
        res = requests.post(f"{BASE_URL}/auth/login", json={"email": new_student_email, "password": "password"})
        if check(res, 200, "Login Student"):
            student_token = res.json()['token']

    # 2. POSTS
    log("=== TESTING POSTS ===")
    res = requests.post(f"{BASE_URL}/posts", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Automated Test Post",
            "content": "This is a test.",
            "scope": "GLOBAL",
            "target_id": None
        }
    )
    check(res, 201, "Create Post (Global)")

    res = requests.get(f"{BASE_URL}/posts", headers={"Authorization": f"Bearer {admin_token}"})
    check(res, 200, "Get Posts")

    # 3. CLASSROOMS
    log("=== TESTING CLASSROOMS ===")
    res = requests.post(f"{BASE_URL}/classroom/create", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Classroom 101",
            "description": "Intro to Testing",
            "max_students": 10
        }
    )
    if check(res, 201, "Create Classroom"):
        classroom_id = res.json()['id']
    
    res = requests.get(f"{BASE_URL}/classroom", headers={"Authorization": f"Bearer {admin_token}"})
    check(res, 200, "List Classrooms")

    if classroom_id and student_token:
        # Join Classroom
        res = requests.post(f"{BASE_URL}/classroom/{classroom_id}/join", 
            headers={"Authorization": f"Bearer {student_token}"}
        )
        check(res, 200, "Student Join Classroom")
        
        # Hand Raise
        res = requests.post(f"{BASE_URL}/classroom/{classroom_id}/hand-raise", 
            headers={"Authorization": f"Bearer {student_token}"}
        )
        check(res, 200, "Student Raise Hand")

    # 4. CHAT
    log("=== TESTING CHAT ===")
    res = requests.post(f"{BASE_URL}/chat/create",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Test Group Chat", "type": "GROUP"}
    )
    if check(res, 201, "Create Group Chat"):
        room_id = res.json()['room']['id']
    
    if room_id:
        res = requests.post(f"{BASE_URL}/chat/message",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"room_id room_id": room_id, "content": "Hello World"} 
        )
        # Wait, JSON payload error in line above? "room_id room_id" -> "room_id"
        # Fixing in next call.
        res = requests.post(f"{BASE_URL}/chat/message",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"room_id": room_id, "content": "Hello World"} 
        )
        check(res, 200, "Send Chat Message")

        res = requests.get(f"{BASE_URL}/chat/messages/{room_id}", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        check(res, 200, "Get Chat Messages")

    # 5. ASSIGNMENTS
    log("=== TESTING ASSIGNMENTS ===")
    if classroom_id:
        # Create Assignment (Admin)
        res = requests.post(f"{BASE_URL}/assignments/create",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Assignment 1",
                "description": "Write something.",
                "due_date": None,
                "classroom_id": classroom_id
            }
        )
        assignment_id = None
        if check(res, 201, "Create Assignment"):
            assignment_id = res.json()['id']
        
        # List Assignments (Student)
        if student_token:
            res = requests.get(f"{BASE_URL}/assignments/{classroom_id}",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            check(res, 200, "List Assignments")
        
        # Submit Assignment (Student)
        if assignment_id and student_token:
            res = requests.post(f"{BASE_URL}/assignments/submit",
                headers={"Authorization": f"Bearer {student_token}"},
                data={"assignment_id": assignment_id, "text_content": "This is my submission."},
                # files={'file': open('test.txt', 'rb')} # Skip file for simple test
            )
            submission_id = None
            if check(res, 200, "Submit Assignment"):
                submission_id = res.json()['id']
            
            # View Submissions (Admin)
            res = requests.get(f"{BASE_URL}/assignments/{assignment_id}/submissions",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            check(res, 200, "View Submissions")

            # Grade Submission (Admin)
            if submission_id:
                 res = requests.post(f"{BASE_URL}/assignments/submission/{submission_id}/grade",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={"grade": "A", "feedback": "Good job"}
                )
                 check(res, 200, "Grade Submission")

    log("=== API VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        log(f"Script Error: {e}", "CRITICAL")
