from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models import User, Token
from app.auth import service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/signup", response_model=dict)
async def signup(user: User) -> dict:
    return await service.signup_user(user)

@router.post("/confirm", response_model=dict)
async def confirm(user: User) -> dict:
    return await service.confirm_user(user)

@router.post("/signin")
async def signin(user: User) -> dict:
    return await service.signin_user(user)

@router.post("/logout", response_model=dict)
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    return await service.logout_user(token)
