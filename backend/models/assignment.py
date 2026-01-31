from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    classroom_id: int

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentResponse(AssignmentBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class SubmissionCreate(BaseModel):
    assignment_id: int
    text_content: Optional[str] = None
    # File handling separate (upload)

class GradeSubmission(BaseModel):
    grade: str
    feedback: Optional[str] = None
