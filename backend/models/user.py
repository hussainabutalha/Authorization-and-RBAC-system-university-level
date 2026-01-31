from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Literal['Admin', 'Faculty', 'Student']
    sub_role: Optional[Literal['Director', 'CampusDirector', 'ProgramCoordinator', 'ITAdmin', 'None']] = 'None'
    department_id: Optional[int] = None
    campus_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    
    # We might need to include included relations like Department/Campus in response
    # For now keep it flat matching the table
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class DBUser(UserResponse):
    password: str # For internal use properly
