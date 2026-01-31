import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from .config import settings

from .utils.security import get_password_hash

class Database:
    pool: asyncpg.Pool = None

    async def connect(self):
        dsn = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        self.pool = await asyncpg.create_pool(dsn)
        print("Database connection pool created.")
        await self.init_db()

    async def init_db(self):
        async with self.pool.acquire() as conn:
            # Create Users Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "users" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) unique NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    sub_role VARCHAR(50),
                    department_id INTEGER,
                    campus_id INTEGER,
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create Campuses Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "campuses" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    location VARCHAR(255),
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create Departments Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "departments" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    code VARCHAR(50),
                    campus_id INTEGER REFERENCES "campuses"(id),
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create Classrooms Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "classrooms" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    max_students INTEGER DEFAULT 50,
                    department_id INTEGER REFERENCES "departments"(id),
                    creator_id INTEGER REFERENCES "users"(id),
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create Classroom Members Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "classroom_members" (
                    id SERIAL PRIMARY KEY,
                    classroom_id INTEGER REFERENCES "classrooms"(id),
                    user_id INTEGER REFERENCES "users"(id),
                    role VARCHAR(50) DEFAULT 'student',
                    is_hand_raised BOOLEAN DEFAULT FALSE,
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now(),
                    UNIQUE(classroom_id, user_id)
                );
            """)

            # Create Assignments Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "assignments" (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    due_date TIMESTAMP,
                    classroom_id INTEGER REFERENCES "classrooms"(id),
                    creator_id INTEGER REFERENCES "users"(id),
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

             # Create Submissions Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "submissions" (
                    id SERIAL PRIMARY KEY,
                    assignment_id INTEGER REFERENCES "assignments"(id),
                    student_id INTEGER REFERENCES "users"(id),
                    text_content TEXT,
                    file_url VARCHAR(255),
                    grade VARCHAR(50),
                    feedback TEXT,
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create Rooms Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "Rooms" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    type VARCHAR(50) DEFAULT 'GROUP', -- GROUP or PERSONAL
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create RoomParticipants Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "RoomParticipants" (
                    id SERIAL PRIMARY KEY,
                    room_id INTEGER REFERENCES "Rooms"(id),
                    user_id INTEGER REFERENCES "users"(id),
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now(),
                    UNIQUE(room_id, user_id)
                );
            """)

            # Create Messages Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "Messages" (
                    id SERIAL PRIMARY KEY,
                    room_id INTEGER REFERENCES "Rooms"(id),
                    sender_id INTEGER REFERENCES "users"(id),
                    content TEXT,
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)

            # Create Posts Table (Updated reference)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS "Posts" (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    author_id INTEGER REFERENCES "users"(id),
                    scope VARCHAR(50),
                    target_id INTEGER,
                    "createdAt" TIMESTAMP DEFAULT now(),
                    "updatedAt" TIMESTAMP DEFAULT now()
                );
            """)
            
            # Seed Admin User if not exists
            admin_email = "director@college.edu"
            exists = await conn.fetchval('SELECT 1 FROM "users" WHERE email = $1', admin_email)
            if not exists:
                hashed_pw = get_password_hash("password") # Default password
                await conn.execute("""
                    INSERT INTO "users" (name, email, password, role, sub_role, "createdAt", "updatedAt")
                    VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                """, "Director User", admin_email, hashed_pw, "Admin", "Director")
                print(f"Seeded Admin User: {admin_email}")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("Database connection pool closed.")

db = Database()

# Dependency for routes to get a connection
async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    async with db.pool.acquire() as connection:
        yield connection
