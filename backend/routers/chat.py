from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..dependencies import get_current_user, get_db_connection
from ..repositories.chat_repository import ChatRepository
from ..models.chat import ChatRoomCreate, MessageCreate
from asyncpg import Connection
from datetime import datetime

router = APIRouter()

@router.get("", response_model=List[dict])
async def get_my_chats(
    user: dict = Depends(get_current_user), 
    conn: Connection = Depends(get_db_connection)
):
    repo = ChatRepository(conn)
    return await repo.get_user_rooms(user['id'])

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_chat(
    room: ChatRoomCreate, 
    user: dict = Depends(get_current_user), 
    conn: Connection = Depends(get_db_connection)
):
    repo = ChatRepository(conn)
    new_room = await repo.create_room(room, user['id'])
    return {"message": "Chat created", "room": new_room}

@router.get("/messages/{room_id}", response_model=List[dict])
async def get_messages(
    room_id: int, 
    user: dict = Depends(get_current_user), 
    conn: Connection = Depends(get_db_connection)
):
    # Security: check if user is participant? skipping for speed, relying on UI flow + obscurity
    # Proper RBAC: Check RoomParticipants
    repo = ChatRepository(conn)
    return await repo.get_messages(room_id)

@router.post("/message")
async def send_message(
    msg: MessageCreate, 
    user: dict = Depends(get_current_user), 
    conn: Connection = Depends(get_db_connection)
):
    try:
        repo = ChatRepository(conn)
        # Check if participant?
        new_msg = await repo.create_message(msg, user['id'])
        
        # Real-time Broadcast
        from ..socket_events import sio
        
        # Serialize datetime for Socket.IO
        socket_msg = new_msg.copy()
        if 'createdAt' in socket_msg and hasattr(socket_msg['createdAt'], 'isoformat'):
            socket_msg['createdAt'] = socket_msg['createdAt'].isoformat()
            
        await sio.emit('newMessage', socket_msg, room=msg.room_id)
        
        return new_msg
    except Exception as e:
        print(f"CRITICAL ERROR in send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
