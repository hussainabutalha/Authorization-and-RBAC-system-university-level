from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ChatRoomCreate(BaseModel):
    name: str
    type: str = "GROUP" # PERSONAL or GROUP
    participant_ids: Optional[List[int]] = []

class MessageCreate(BaseModel):
    room_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    createdAt: datetime
    Sender: Optional[Dict] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
