from fastapi import Depends, HTTPException
from decimal import Decimal

from app.user import utils as user_utils
from app.asset import service as asset_service
from app.liability import service as liability_service
from app.models import AssetBase, LiabilityBase

def calculate_portfolio(current_user: dict = Depends(user_utils.get_current_user_id)):
    """
    Calculates total assets, liabilities, and net worth for a user.
    """
    try:
        # Fetch raw data
        raw_assets = asset_service.list_assets_per_user(current_user)
        raw_liabilities = liability_service.list_liabilities_per_user(current_user)

        # Typecast to Pydantic models
        assets = [AssetBase(**a) for a in raw_assets]
        liabilities = [LiabilityBase(**l) for l in raw_liabilities]

        # Compute totals
        total_assets = sum(Decimal(str(a.asset_value)) for a in assets)
        total_liabilities = sum(Decimal(str(l.liability_value)) for l in liabilities)
        net_worth = total_assets - total_liabilities

        return {
            "total_assets": float(total_assets),
            "total_liabilities": float(total_liabilities),
            "net_worth": float(net_worth),
            "assets": assets,
            "liabilities": liabilities
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
