from asyncpg import Connection
from ..models.assignment import AssignmentCreate, SubmissionCreate, GradeSubmission
from datetime import datetime
from typing import List

class AssignmentRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def create(self, assignment: AssignmentCreate, creator_id: int):
        query = """
            INSERT INTO "assignments" (title, description, due_date, classroom_id, creator_id, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, "createdAt", "updatedAt"
        """
        now = datetime.now()
        row = await self.conn.fetchrow(
            query,
            assignment.title,
            assignment.description,
            assignment.due_date,
            assignment.classroom_id,
            creator_id,
            now,
            now
        )
        return {**assignment.dict(), "creator_id": creator_id, **dict(row)}

    async def get_by_classroom(self, classroom_id: int):
        query = """
            SELECT * FROM "assignments"
            WHERE classroom_id = $1
            ORDER BY "createdAt" DESC
        """
        rows = await self.conn.fetch(query, classroom_id)
        return [dict(row) for row in rows]

    async def submit(self, submission: SubmissionCreate, student_id: int, file_url: str = None):
        # Check integrity
        # Insert
        query = """
            INSERT INTO "submissions" (assignment_id, student_id, text_content, file_url, "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        now = datetime.now()
        row = await self.conn.fetchrow(
            query, 
            submission.assignment_id,
            student_id,
            submission.text_content,
            file_url,
            now,
            now
        )
        return dict(row)

    async def get_submissions(self, assignment_id: int):
        query = """
            SELECT s.*, u.name as student_name
            FROM "submissions" s
            JOIN "users" u ON s.student_id = u.id
            WHERE s.assignment_id = $1
        """
        rows = await self.conn.fetch(query, assignment_id)
        
        results = []
        for row in rows:
            data = dict(row)
            data["Student"] = {"name": row['student_name']} # Match frontend structure
            results.append(data)
        return results

    async def grade(self, submission_id: int, grade_data: GradeSubmission):
        query = """
            UPDATE "submissions"
            SET grade = $1, feedback = $2, "updatedAt" = $3
            WHERE id = $4
        """
        now = datetime.now()
        await self.conn.execute(query, grade_data.grade, grade_data.feedback, now, submission_id)
        return True
