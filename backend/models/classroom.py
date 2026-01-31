from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ClassroomBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_students: Optional[int] = 50
    department_id: Optional[int] = None

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomResponse(ClassroomBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    department: Optional[Dict] = None
    Members: Optional[List[Dict]] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ClassroomJoin(BaseModel):
    pass
