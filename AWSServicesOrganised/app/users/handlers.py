from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer

from app.users import service as user_service
from app.users import utils as user_utils

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/allusers")
async def get_all_users() -> dict:
    return user_service.list_users()

@router.post("/profile/upload-pic", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: dict = Depends(user_utils.get_current_user)
    ):
    return user_service.upload_pic(file, current_user)

    