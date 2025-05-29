from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer

from app.user import service as user_service
from app.user import utils as user_utils
from app.models import UserProfile, UserProfileFull


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/profile/picture", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    return user_service.upload_pic(file, current_user)


@router.get("/profile/picture", response_model=dict)
async def get_profile_picture(
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    return user_service.get_profile_picture(current_user)


@router.put("/profile", response_model=dict)
async def update_profile_details(
    profile: UserProfile,
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    return user_service.update_profile_details(profile, current_user)


@router.get("/profile", response_model=UserProfileFull)
async def get_profile_details(
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    return user_service.get_profile_details(current_user)
