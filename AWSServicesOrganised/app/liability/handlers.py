from fastapi import APIRouter, Depends, Path
from typing import Annotated

from app.user import utils as user_utils
from app.liability import service as liability_service
from app.models import LiabilityBase, Liability

router = APIRouter()

@router.post("/")
def add_liability(
    data: LiabilityBase, 
    user=Depends(user_utils.get_current_user_id)
):
    return liability_service.create_liability(data, user)

@router.get("/", response_model=list[Liability])
def get_all_liabilities(user=Depends(user_utils.get_current_user_id)):
    return liability_service.list_liabilities_per_user(user)

@router.get("/{liability_id}")
def get_one_liability(
    liability_id: Annotated[str | None, Path()],
    user=Depends(user_utils.get_current_user_id)
):
    return liability_service.get_liability_by_id(liability_id, user)

@router.delete("/{liability_id}")
def delete_one_liability(
    liability_id: str,
    user=Depends(user_utils.get_current_user_id)
):
    return liability_service.delete_liability(liability_id, user)

@router.delete("/")
def delete_all_liabilities(user=Depends(user_utils.get_current_user_id)):
    return liability_service.delete_all_liabilities(user)
