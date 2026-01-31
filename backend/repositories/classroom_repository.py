from asyncpg import Connection
from ..models.classroom import ClassroomCreate
from datetime import datetime
from typing import Optional

class ClassroomRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def create(self, classroom: ClassroomCreate, creator_id: int):
        query = """
            INSERT INTO "classrooms" (name, description, max_students, department_id, creator_id, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, "createdAt", "updatedAt"
        """
        now = datetime.now()
        row = await self.conn.fetchrow(
            query,
            classroom.name,
            classroom.description,
            classroom.max_students,
            classroom.department_id,
            creator_id,
            now,
            now
        )
        return {**classroom.dict(), "creator_id": creator_id, **dict(row)}

    async def get_all(self, user_id: int, role: str):
        # Logic: 
        # If Admin, return all (maybe filtered by Dept later). 
        # If Student/Faculty, return all (assuming public directory) OR just enrolled ones?
        # Implementation in Legacy `loadClassrooms` seemed to fetch all, and `canJoin` checked membership.
        # But `loadClassrooms` endpoint in legacy might restrict.
        # Let's return ALL for now to match "Directory" style, enabling join.
        
        # We need to fetch basic info + Dept Name + Member Count + Creator Name?
        # And also fetch if current user is member? Or just raw list.
        # The frontend expects: `department.name`, `Members` (list/count).
        
        query = """
            SELECT 
                c.id, c.name, c.description, c.max_students, c.department_id, c.creator_id,
                d.name as department_name,
                u.name as creator_name
            FROM "classrooms" c
            LEFT JOIN "departments" d ON c.department_id = d.id
            LEFT JOIN "users" u ON c.creator_id = u.id
            ORDER BY c."createdAt" DESC
        """
        rows = await self.conn.fetch(query)
        
        results = []
        for row in rows:
            data = dict(row)
            # Fetch Members for each classroom (efficiently? No, N+1 query for now, acceptable for low usage)
            # Or use a join/agg.
            # Frontend relies on `Members` array array length.
            
            members_query = """
                SELECT u.id, u.name, u.email, cm.role, cm.is_hand_raised
                FROM "classroom_members" cm
                JOIN "users" u ON cm.user_id = u.id
                WHERE cm.classroom_id = $1
            """
            members = await self.conn.fetch(members_query, row['id'])
            
            data['department'] = {'name': row['department_name']} if row['department_name'] else None
            data['Creator'] = {'name': row['creator_name']}
            data['Members'] = [dict(m) for m in members]
            
            # Formate response as frontend expects
            results.append(data)
            
        return results

    async def get_by_id(self, classroom_id: int):
        query = """
            SELECT 
                c.id, c.name, c.description, c.max_students, c.department_id, c.creator_id,
                d.name as department_name,
                u.name as creator_name
            FROM "classrooms" c
            LEFT JOIN "departments" d ON c.department_id = d.id
            LEFT JOIN "users" u ON c.creator_id = u.id
            WHERE c.id = $1
        """
        row = await self.conn.fetchrow(query, classroom_id)
        if not row:
            return None
            
        data = dict(row)
        
        members_query = """
            SELECT u.id, u.name, u.email, cm.role, cm.is_hand_raised
            FROM "classroom_members" cm
            JOIN "users" u ON cm.user_id = u.id
            WHERE cm.classroom_id = $1
        """
        members = await self.conn.fetch(members_query, classroom_id)
        
        data['department'] = {'name': row['department_name']} if row['department_name'] else None
        data['Creator'] = {'name': row['creator_name']}
        
        # Frontend logic uses `member.ClassroomMember.role` and `is_hand_raised`.
        # backend returns flat list. Frontend code:
        # `const currentMember = classroom.Members?.find(m => m.id === currentUser.id);`
        # `isStudent = currentMember && currentMember.ClassroomMember.role === 'student';`
        # Wait, frontend expects `ClassroomMember` nested object?
        # `member.ClassroomMember?.role`.
        # My N+1 query above returns flat fields.
        # I should structure the `Members` list to have `ClassroomMember` key if I want to match legacy exactly,
        # OR I should fix the frontend.
        # Let's fix the backend to return what frontend expects: a dictionary with `ClassroomMember` object.
        
        formatted_members = []
        for m in members:
            m_dict = dict(m)
            formatted_members.append({
                "id": m_dict['id'],
                "name": m_dict['name'],
                "email": m_dict['email'],
                "ClassroomMember": {
                    "role": m_dict['role'],
                    "is_hand_raised": m_dict['is_hand_raised']
                }
            })
            
        data['Members'] = formatted_members
        return data

    async def join(self, classroom_id: int, user_id: int, role: str):
        # Check if already member
        check = 'SELECT 1 FROM "classroom_members" WHERE classroom_id = $1 AND user_id = $2'
        exists = await self.conn.fetchval(check, classroom_id, user_id)
        if exists:
            return False
            
        query = """
            INSERT INTO "classroom_members" (classroom_id, user_id, role, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5)
        """
        now = datetime.now()
        await self.conn.execute(query, classroom_id, user_id, role, now, now)
        return True

    async def toggle_hand(self, classroom_id: int, user_id: int):
        # Toggle boolean
        query = """
            UPDATE "classroom_members"
            SET is_hand_raised = NOT is_hand_raised
            WHERE classroom_id = $1 AND user_id = $2
            RETURNING is_hand_raised
        """
        val = await self.conn.fetchval(query, classroom_id, user_id)
        return val
