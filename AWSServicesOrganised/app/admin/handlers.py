from fastapi import APIRouter, Depends, Request
from typing import Optional

from app.admin import service as admin_service
from app.user import utils as user_utils


router = APIRouter()

@router.get("/users")
async def list_all_users(
    request: Request,    
    current_user: dict = Depends(user_utils.require_admin)
    ) -> dict:
    return admin_service.get_all_users_cognito_userpool(request) 


@router.get("/users/by-email/{email}")
async def get_user_by_email(
    request: Request,    
    email: str,
    current_user: dict = Depends(user_utils.require_admin),
    ) -> dict:
    return admin_service.get_user_by_email(email, request)


@router.get("/users/by-username/{username}")
async def get_user_by_username(
    request: Request,
    username: str,
    current_user: dict = Depends(user_utils.require_admin),
    ) -> dict:
    return admin_service.get_user_by_username(username, request)
