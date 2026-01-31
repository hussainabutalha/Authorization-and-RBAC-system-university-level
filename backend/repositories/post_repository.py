from asyncpg import Connection
from ..models.post import PostCreate
from datetime import datetime
from typing import Optional

class PostRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def create(self, post: PostCreate, author_id: int):
        # Handle target_id empty logic here if not handled in route/model
        # But Pydantic handles validation, so route handles logic.
        
        query = """
            INSERT INTO "Posts" (title, content, author_id, scope, target_id, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, "createdAt", "updatedAt"
        """
        now = datetime.now()
        row = await self.conn.fetchrow(
            query,
            post.title,
            post.content,
            author_id,
            post.scope,
            post.target_id,
            now,
            now
        )
        return {**post.dict(), "author_id": author_id, **dict(row)}

    async def get_all(self, scope: Optional[str] = None, target_id: Optional[int] = None):
        query = 'SELECT * FROM "Posts" WHERE 1=1'
        args = []
        i = 1
        
        if scope:
            query += f' AND scope = ${i}'
            args.append(scope)
            i += 1
        
        if target_id is not None:
            query += f' AND target_id = ${i}'
            args.append(target_id)
            i += 1
            
        query += ' ORDER BY "createdAt" DESC'
        
        rows = await self.conn.fetch(query, *args)
        return [dict(row) for row in rows]
