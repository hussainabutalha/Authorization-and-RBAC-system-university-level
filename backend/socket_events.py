import socketio
from socketio import AsyncRedisManager
from .config import settings

args = {'async_mode': 'asgi', 'cors_allowed_origins': '*'}

if settings.REDIS_URL:
    mgr = AsyncRedisManager(settings.REDIS_URL)
    args['client_manager'] = mgr
    print(f"Socket.IO using Redis Adapter: {settings.REDIS_URL}")

sio = socketio.AsyncServer(**args)

@sio.event
async def connect(sid, environ):
    print(f"New client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def joinRoom(sid, room):
    sio.enter_room(sid, room)
    print(f"Socket {sid} joined room {room}")

@sio.event
async def leaveRoom(sid, room):
    sio.leave_room(sid, room)
    print(f"Socket {sid} left room {room}")

@sio.event
async def sendMessage(sid, data):
    # data = { room_id, message, sender_id, sender_name, timestamp }
    # Broadcast to room
    print(f"Broadcasting message to {data['room_id']}")
    await sio.emit('newMessage', data, room=data['room_id'])
