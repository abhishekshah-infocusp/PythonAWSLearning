import boto3
import uuid
import datetime
import logging

from fastapi import Depends, HTTPException
from decimal import Decimal

from app.models import AssetBase
from app.user import utils as user_utils
from app.config import REGION, DynamoDB_ASSET_DETAILS_TABLE


logger = logging.getLogger(__name__)


def create_asset(
        asset: AssetBase,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Creates a new asset in DynamoDB with the provided asset details.
    """
    try:
        logger.info(f"Creating asset for user: {current_user.get('username')}")
        asset_id = str(uuid.uuid4()) 
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)

        item = {
            "asset_id": asset_id,
            "username": current_user["username"],
            "category": asset.category,
            "title": asset.title,
            "asset_value": Decimal(str(asset.asset_value)),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "sub": current_user["sub"],
            "identity_id": identity_id
        }
        table.put_item(Item=item)
        logger.info(f"Asset created successfully with ID: {asset_id}")
    except Exception as e:
        logger.error(f"Error creating asset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))    
    logger.info(f"Asset created successfully for user: {current_user.get('username')}")
    return {"Asset created successfully"}


def list_assets_per_user(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Lists all assets for a given user.
    """
    try:
        logger.info(f"Listing assets for user: {current_user.get('username')}")
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)

        response = table.query(
            IndexName='UserSubIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(current_user['username'])
        )
        logger.info(f"Assets listed successfully for user: {current_user.get('username')}")
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_asset_by_id(
        asset_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Retrieves a specific asset by its ID.
    """
    try:
        logger.info(f"Fetching asset with ID: {asset_id} for user: {current_user.get('username')}")
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)

        response = table.get_item(
            Key={
                "asset_id": asset_id
            }
        )
        
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Asset not found")
        logger.info(f"Asset with ID: {asset_id} fetched successfully for user: {current_user.get('username')}")
        return response['Item']
    except Exception as e:
        logger.error(f"Error fetching asset by ID: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def delete_asset(
        asset_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Deletes a specific asset by its ID.
    """
    try:
        logger.info(f"Deleting asset with ID: {asset_id} for user: {current_user.get('username')}")
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)
        response = table.delete_item(
            Key={
                "asset_id": asset_id
            }
        )
        logger.info(f"Asset with ID: {asset_id} deleted successfully for user: {current_user.get('username')}")
        return {"message": "Asset deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting asset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def delete_all_assets(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Deletes all assets for a given user.
    """
    try:
        logger.info(f"Deleting all assets for user: {current_user.get('username')}")
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)

        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(current_user['username'])
        )
        
        for item in response.get('Items', []):
            table.delete_item(
                Key={
                    "asset_id": item['asset_id'],
                    "username": current_user["username"]
                }
            )
        logger.info(f"All assets deleted successfully for user: {current_user.get('username')}")
        return {"message": "All assets deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting all assets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))