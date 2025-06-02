import boto3
import uuid
import datetime

from fastapi import Depends, HTTPException
from decimal import Decimal

from app.models import AssetBase
from app.user import utils as user_utils
from app.config import REGION, DynamoDB_ASSET_DETAILS_TABLE

def create_asset(
        asset: AssetBase,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Creates a new asset in DynamoDB with the provided asset details.
    """
    try:
        print(current_user.keys())
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

    return {"Asset created successfully"}


def list_assets_per_user(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Lists all assets for a given user.
    """
    try:
        print("HI", current_user.keys())
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)
        print(table.key_schema)

        response = table.query(
            IndexName='UserSubIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(current_user['username'])
        )
        
        return response.get('Items', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_asset_by_id(
        asset_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Retrieves a specific asset by its ID.
    """
    try:
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
        
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_asset(
        asset_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Deletes a specific asset by its ID.
    """
    try:
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_ASSET_DETAILS_TABLE)
        print("Deleting asset with ID:", asset_id)
        response = table.delete_item(
            Key={
                "asset_id": asset_id
            }
        )
        
        return {"message": "Asset deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_all_assets(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Deletes all assets for a given user.
    """
    try:
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
        
        return {"message": "All assets deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))