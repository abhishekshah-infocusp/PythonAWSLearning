from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordBearer

from app.models import UserSignUp, UserConfirm, UserSignIn, Token
from app.auth import service
from app.user import utils as user_utils

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/signup", response_model=dict)
async def signup(user: UserSignUp) -> dict:
    return await service.signup_user(user)


@router.post("/confirm", response_model=dict)
async def confirm(user: UserConfirm) -> dict:
    return await service.confirm_user(user)


@router.post("/signin", response_model=dict)
async def signin(user: UserSignIn, response: Response) -> dict:
    return await service.signin_user(user, response)


@router.post("/logout", response_model=dict)
async def logout(current_user: dict = Depends(user_utils.get_current_user_id),
) -> dict:
    return await service.logout_user(current_user)
