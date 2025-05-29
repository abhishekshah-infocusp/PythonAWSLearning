from fastapi import APIRouter, Depends

from app.user import utils as user_utils
from app.asset import service as asset_service
from app.models import AssetBase

router = APIRouter()



@router.post("/")
def add_asset(
    data: AssetBase, 
    user=Depends(user_utils.get_current_user)
    ):
    return asset_service.create_asset(data, user)


# @router.get("/")
# def get_all_assets(user=Depends(user_utils.get_current_user)):
#     return asset_service.list_assets(user["username"])


# @router.get("/{asset_id}")
# def get_one_asset(asset_id: str, user=Depends(user_utils.get_current_user)):
#     return asset_service.get_asset(asset_id, user["username"])


# @router.put("/{asset_id}")
# def update_one_asset(asset_id: str, data: AssetUpdate, user=Depends(user_utils.get_current_user)):
#     return asset_service.update_asset(asset_id, data, user["username"])


# @router.delete("/{asset_id}")
# def delete_one_asset(asset_id: str, user=Depends(user_utils.get_current_user)):
#     return asset_service.delete_asset(asset_id, user["username"])
