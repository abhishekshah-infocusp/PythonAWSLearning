from fastapi import APIRouter, Depends
from app.portfolio import service as portfolio_service
from app.user import utils as user_utils

router = APIRouter()

@router.get("/")
def get_portfolio(current_user=Depends(user_utils.get_current_user_id)):
    return portfolio_service.calculate_portfolio(current_user)
