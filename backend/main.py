from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import socketio

from .database import db
from .routers import auth, posts, classroom, chat, assignment
from .socket_events import sio


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


# Socket.IO setup (AsyncServer)
socket_app = socketio.ASGIApp(sio)

app = FastAPI(
    title="Authorization & RBAC System",
    description="University-level Role-Based Access Control API",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Socket.IO app
app.mount("/socket.io", socket_app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(classroom.router, prefix="/classroom", tags=["Classroom"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(assignment.router, prefix="/assignments", tags=["Assignments"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
