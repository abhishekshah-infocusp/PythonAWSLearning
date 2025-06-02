from fastapi import APIRouter, Depends, Query, Path
from typing import Annotated

from app.user import utils as user_utils
from app.asset import service as asset_service
from app.models import AssetBase, Asset

router = APIRouter()

@router.post("/")
def add_asset(
    data: AssetBase, 
    user=Depends(user_utils.get_current_user_id)
    ):
    return asset_service.create_asset(data, user)

@router.get("/", response_model=list[Asset])
def get_all_assets(user=Depends(user_utils.get_current_user_id)):
    return asset_service.list_assets_per_user(user)

@router.get("/{asset_id}")
def get_one_asset(
    asset_id: Annotated[str| None, Path()], 
    user=Depends(user_utils.get_current_user_id)):
    return asset_service.get_asset_by_id(asset_id, user)

@router.delete("/{asset_id}")
def delete_one_asset(
    asset_id: str, 
    user=Depends(user_utils.get_current_user_id)):
    return asset_service.delete_asset(asset_id, user)

