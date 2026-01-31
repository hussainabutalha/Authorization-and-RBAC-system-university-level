from asyncpg import Connection
from ..models.chat import ChatRoomCreate, MessageCreate
from datetime import datetime
from typing import List

class ChatRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def get_user_rooms(self, user_id: int):
        query = """
            SELECT r.id, r.name, r.type
            FROM "Rooms" r
            JOIN "RoomParticipants" rp ON r.id = rp.room_id
            WHERE rp.user_id = $1
            ORDER BY r."updatedAt" DESC
        """
        rows = await self.conn.fetch(query, user_id)
        return [dict(row) for row in rows]

    async def create_room(self, room: ChatRoomCreate, creator_id: int):
        # 1. Create Room
        query = """
            INSERT INTO "Rooms" (name, type, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $3)
            RETURNING id, name, type
        """
        now = datetime.now()
        row = await self.conn.fetchrow(query, room.name, room.type, now)
        room_id = row['id']

        # 2. Add Participants (Creator + others)
        participants = set(room.participant_ids)
        participants.add(creator_id)
        
        args = [(room_id, uid, now, now) for uid in participants]
        await self.conn.executemany("""
            INSERT INTO "RoomParticipants" (room_id, user_id, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4)
            ON CONFLICT DO NOTHING
        """, args)
        
        return dict(row)

    async def create_message(self, message: MessageCreate, sender_id: int):
        query = """
            INSERT INTO "Messages" (room_id, sender_id, content, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $4)
            RETURNING id, "createdAt"
        """
        now = datetime.now()
        row = await self.conn.fetchrow(query, message.room_id, sender_id, message.content, now)
        
        # Update Room updatedAt
        await self.conn.execute('UPDATE "Rooms" SET "updatedAt" = $1 WHERE id = $2', now, message.room_id)
        
        # Fetch Sender Info to return full object for Socket broadcast
        sender_row = await self.conn.fetchrow('SELECT name, email FROM "users" WHERE id = $1', sender_id)
        
        return {
            "id": row['id'],
            "room_id": message.room_id,
            "sender_id": sender_id,
            "content": message.content,
            "createdAt": row['createdAt'],
            "Sender": {
                "name": sender_row['name'],
                "email": sender_row['email']
            }
        }

    async def get_messages(self, room_id: int):
        query = """
            SELECT m.id, m.room_id, m.sender_id, m.content, m."createdAt",
                   u.name as sender_name, u.email as sender_email
            FROM "Messages" m
            JOIN "users" u ON m.sender_id = u.id
            WHERE m.room_id = $1
            ORDER BY m."createdAt" ASC
        """
        rows = await self.conn.fetch(query, room_id)
        results = []
        for row in rows:
            data = dict(row)
            data['Sender'] = {"name": row['sender_name'], "email": row['sender_email']}
            results.append(data)
        return results
