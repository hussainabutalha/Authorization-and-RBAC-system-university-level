from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from ..dependencies import get_current_user, get_db_connection
from ..repositories.assignment_repository import AssignmentRepository
from ..models.assignment import AssignmentCreate, SubmissionCreate, GradeSubmission
from asyncpg import Connection
import os
import shutil

router = APIRouter()

# Directory for uploads
UPLOAD_DIR = "public/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    if user['role'] == 'Student':
         raise HTTPException(status_code=403, detail="Students cannot create assignments")
    repo = AssignmentRepository(conn)
    return await repo.create(assignment, user['id'])

@router.get("/{classroom_id}", response_model=List[dict])
async def get_assignments(
    classroom_id: int,
    user: dict = Depends(get_current_user), # Any member can view?
    conn: Connection = Depends(get_db_connection)
):
    repo = AssignmentRepository(conn)
    return await repo.get_by_classroom(classroom_id)

@router.post("/submit")
async def submit_assignment(
    assignment_id: int = Form(...),
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    file_url = None
    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_url = f"/uploads/{file.filename}" # Relative to public/
    
    submission = SubmissionCreate(assignment_id=assignment_id, text_content=text_content)
    repo = AssignmentRepository(conn)
    return await repo.submit(submission, user['id'], file_url)

@router.get("/{assignment_id}/submissions", response_model=List[dict])
async def get_submissions(
    assignment_id: int,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    # Only Admin/Faculty/Creator should see submissions
    if user['role'] == 'Student':
         raise HTTPException(status_code=403, detail="Unauthorized")
         
    repo = AssignmentRepository(conn)
    return await repo.get_submissions(assignment_id)

@router.post("/submission/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    grade_data: GradeSubmission,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    if user['role'] == 'Student':
         raise HTTPException(status_code=403, detail="Unauthorized")
    repo = AssignmentRepository(conn)
    await repo.grade(submission_id, grade_data)
    return {"message": "Graded"}
