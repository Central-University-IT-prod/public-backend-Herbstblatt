from datetime import datetime, timezone, timedelta
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError


SECRET_KEY = os.getenv("RANDOM_SECRET", "")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="auth/sign-in")


def gen_token(user_id: int):
    data = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    return jwt.encode(data, SECRET_KEY)


async def get_user_id(token: Annotated[str, Depends(oauth_scheme)]) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = None
    try:
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return int(user_id)
