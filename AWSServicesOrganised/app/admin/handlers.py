from fastapi import APIRouter, Depends
from app.admin import service as admin_service
from app.user import utils as user_utils

router = APIRouter()

@router.get("/get-all-users-cognito-userpool")
async def get_all_users_cognito_userpool(
    current_user: dict = Depends(user_utils.get_current_user),
    is_admin_user: bool = Depends(user_utils.is_admin)
) -> dict:
    if is_admin_user:
        return admin_service.get_all_users_cognito_userpool() 
    else:
        raise HTTPException(status_code=403, detail="You do not have Admin permission to access this resource.") 
