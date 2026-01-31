from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from .config import settings
from .database import get_db_connection
from .repositories.user_repository import UserRepository
from asyncpg import Connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token-swagger")

async def get_current_user(token: str = Depends(oauth2_scheme), conn: Connection = Depends(get_db_connection)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub") # Assuming sub holds email or id. Node.js code put entire user object. 
        # Node code: jwt.sign({ id, role, sub_role... }, ...)
        # So payload has `id`, `role`, etc.
        
        # Let's verify what we put in token in auth router later.
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    repo = UserRepository(conn)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user # Dict
