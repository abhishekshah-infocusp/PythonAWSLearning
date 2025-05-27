from fastapi import APIRouter, Depends
from typing import Optional

from app.admin import service as admin_service
from app.user import utils as user_utils

router = APIRouter()

@router.get("/users")
async def list_all_users(
    current_user: dict = Depends(user_utils.require_admin),
) -> dict:
    return admin_service.get_all_users_cognito_userpool() 


@router.get("/users/by-email/{email}")
async def get_user_by_email(
    email: str,
    current_user: dict = Depends(user_utils.require_admin),
) -> dict:
    return admin_service.get_user_by_email(email)


@router.get("/users/by-username/{username}")
async def get_user_by_username(
    username: str,
    current_user: dict = Depends(user_utils.require_admin),
) -> dict:
    return admin_service.get_user_by_username(username)
