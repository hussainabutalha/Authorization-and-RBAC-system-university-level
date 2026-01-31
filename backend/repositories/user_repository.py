from asyncpg import Connection
from ..models.user import UserCreate, DBUser
from datetime import datetime

class UserRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def get_by_email(self, email: str):
        query = 'SELECT * FROM "users" WHERE email = $1' 
        row = await self.conn.fetchrow(query, email)
        if row:
            return dict(row)
        return None

    async def get_by_id(self, user_id: int):
        query = 'SELECT * FROM "users" WHERE id = $1'
        row = await self.conn.fetchrow(query, user_id)
        if row:
            return dict(row)
        return None

    async def create(self, user: UserCreate):
        query = """
            INSERT INTO "users" (name, email, password, role, sub_role, department_id, campus_id, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, "createdAt", "updatedAt"
        """
        now = datetime.now()
        row = await self.conn.fetchrow(
            query, 
            user.name, 
            user.email, 
            user.password, 
            user.role, 
            user.sub_role, 
            user.department_id, 
            user.campus_id,
            now,
            now
        )
        return {**user.dict(), **dict(row)}
