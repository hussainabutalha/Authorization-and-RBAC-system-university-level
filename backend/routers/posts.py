from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ..dependencies import get_current_user, get_db_connection
from ..repositories.post_repository import PostRepository
from ..models.post import PostCreate, PostResponse
from asyncpg import Connection
from pydantic import validator

# Patch PostCreate to handle empty string for target_id
class LegacyPostCreate(PostCreate):
    @validator('target_id', pre=True)
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    post: LegacyPostCreate, 
    user: dict = Depends(get_current_user), 
    conn: Connection = Depends(get_db_connection)
):
    # RBAC LOGIC (can_post_to_scope port)
    role = user.get("role")
    sub_role = user.get("sub_role")
    dept_id = user.get("department_id")
    campus_id = user.get("campus_id")
    
    scope = post.scope
    target_id = post.target_id

    allowed = False
    
    # 3.3 Director: Full Academic Control
    if role == 'Admin' and sub_role == 'Director':
        allowed = True
    # 3.4 IT Admin
    elif role == 'Admin' and sub_role == 'IT_Admin': # Check DB value exact text 'ITAdmin' or 'IT_Admin'
        # Node legacy checked 'IT_Admin', but DB might handle it.
        # User list showed 'ITAdmin' is NOT 'IT_Admin' maybe? 
        # reproduction script showed 'ProgramCoordinator'.
        # Let's assume standard 'ITAdmin' if legacy code used it.
        # Looking at Node `rbacMiddleware.js`: `if (role === 'Admin' && sub_role === 'IT_Admin')`
        # BUT models likely store ENUM. 
        # Valid sub_roles: 'Director', 'CampusDirector', 'ProgramCoordinator', 'ITAdmin', 'None'
        # Node middleware had 'IT_Admin'? I viewed it earlier...
        # Line 36: `if (role === 'Admin' && sub_role === 'IT_Admin')`
        # Line 82: `if (req.user.sub_role === 'ITAdmin')`
        # Discrepancy in Node code! 
        # I will allow both to be safe.
        allowed = True
    elif role == 'Admin' and (sub_role == 'ITAdmin' or sub_role == 'IT_Admin'):
        allowed = True
        
    # 3.2 Campus Director
    elif role == 'Admin' and sub_role == 'CampusDirector':
        if scope == 'CAMPUS' and target_id == campus_id:
            allowed = True
            
    # 3.1 Program Coordinator
    elif role == 'Admin' and sub_role == 'ProgramCoordinator':
        if scope == 'DEPARTMENT' and target_id == dept_id:
            allowed = True
            
    # Classrooms
    elif scope == 'CLASSROOM':
        if role == 'Admin' or role == 'Faculty':
            allowed = True
            
    if not allowed:
        raise HTTPException(status_code=403, detail="Access Denied: You do not have permission to post to this scope/target.")

    repo = PostRepository(conn)
    new_post = await repo.create(post, user["id"])
    return new_post

@router.get("", response_model=List[dict])
async def get_posts(
    scope: Optional[str] = None, 
    target_id: Optional[int] = None,
    user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db_connection)
):
    repo = PostRepository(conn)
    posts = await repo.get_all(scope, target_id)
    return posts
