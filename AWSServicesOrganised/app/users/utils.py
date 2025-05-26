from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.auth import service as auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_info = await auth_service.verify_token(token)
    if not user_info:
        raise HTTpException(status_code=401, detail="Invalid credentials")
    return user_info


