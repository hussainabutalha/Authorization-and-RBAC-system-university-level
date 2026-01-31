from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    scope: Literal['GLOBAL', 'CAMPUS', 'DEPARTMENT', 'CLASSROOM']
    target_id: Optional[int] = None # Can be Int or Null

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author_id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
