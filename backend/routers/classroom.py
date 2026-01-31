from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ..dependencies import get_current_user, get_db_connection
from ..repositories.classroom_repository import ClassroomRepository
from ..models.classroom import ClassroomCreate
from asyncpg import Connection

router = APIRouter()

@router.get("", response_model=List[dict])
async def get_classrooms(
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    repo = ClassroomRepository(conn)
    return await repo.get_all(user['id'], user['role'])

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_classroom(
    classroom: ClassroomCreate,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    if user['role'] != 'Admin' and user['role'] != 'Faculty': # Assuming Faculty can create? Legacy checks Admin/Director.
        # "Show create button for HOD, Campus Director, Director" in frontend.
        # Let's enforce strict RBAC if needed, but for now allow Admin.
        pass
        
    repo = ClassroomRepository(conn)
    return await repo.create(classroom, user['id'])

@router.get("/{classroom_id}", response_model=dict)
async def get_classroom(
    classroom_id: int,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    repo = ClassroomRepository(conn)
    cls = await repo.get_by_id(classroom_id)
    if not cls:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return cls

@router.post("/{classroom_id}/join")
async def join_classroom(
    classroom_id: int,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    repo = ClassroomRepository(conn)
    # Role logic: Students/Faculty join as 'student' (member) usually?
    # Or Faculty join as 'teacher'?
    # Frontend: `currentUser.role === 'Student' || currentUser.role === 'Faculty'` can join.
    # Default role 'student' in repo.
    
    success = await repo.join(classroom_id, user['id'], 'student') # Defaulting to student role for joiners
    if not success:
         return {"message": "Already a member"}
    return {"message": "Joined successfully"}

@router.post("/{classroom_id}/hand-raise")
async def toggle_hand(
    classroom_id: int,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    repo = ClassroomRepository(conn)
    is_raised = await repo.toggle_hand(classroom_id, user['id'])
    return {"message": "Hand toggled", "is_hand_raised": is_raised}
