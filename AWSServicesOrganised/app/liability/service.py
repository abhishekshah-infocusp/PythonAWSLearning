import boto3
import uuid
import datetime
import logging

from fastapi import Depends, HTTPException
from decimal import Decimal

from app.models import LiabilityBase
from app.user import utils as user_utils
from app.config import REGION, DynamoDB_LIABILITY_DETAILS_TABLE


logger = logging.getLogger(__name__)


def create_liability(
        liability: LiabilityBase,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        logger.info(f"Creating liability for user: {current_user.get('user_id')}")
        liability_id = str(uuid.uuid4())
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        item = {
            "liability_id": liability_id,
            "username": current_user["username"],
            "category": liability.category,
            "title": liability.title,
            "liability_value": Decimal(str(liability.liability_value)),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "sub": current_user["sub"],
            "identity_id": identity_id
        }
        table.put_item(Item=item)
        logger.info(f"Liability created successfully with ID: {liability_id}")
        return {"Liability created successfully"}
    except Exception as e:
        logger.error(f"Error creating liability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def list_liabilities_per_user(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        logger.info(f"Listing liabilities for user: {current_user.get('user_id')}")
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        response = table.query(
            IndexName="UserSubIndex",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(current_user['username'])
        )
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Error listing liabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_liability_by_id(
        liability_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        logger.info(f"Fetching liability with ID: {liability_id} for user: {current_user.get('user_id')}")
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        response = table.get_item(
            Key={"liability_id": liability_id}
        )
        item = response.get("Item")
        if not item:
            logger.warning(f"Liability with ID: {liability_id} not found for user: {current_user.get('user_id')}")
            raise HTTPException(status_code=404, detail="Liability not found")
        if item.get("sub") != current_user["sub"]:
            logger.warning(f"Unauthorized access attempt to liability ID: {liability_id} by user: {current_user.get('user_id')}")
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return item
    except Exception as e:
        logger.error(f"Error fetching liability by ID: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def delete_liability(
        liability_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        logger.info(f"Deleting liability with ID: {liability_id} for user: {current_user.get('user_id')}")
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        table.delete_item(Key={"liability_id": liability_id})
        logger.info(f"Liability with ID: {liability_id} deleted successfully for user: {current_user.get('user_id')}")
        return {"message": "Liability deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting liability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def delete_all_liabilities(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        logger.info(f"Deleting all liabilities for user: {current_user.get('user_id')}")
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(current_user['username'])
        )
        for item in response.get('Items', []):
            table.delete_item(Key={"liability_id": item['liability_id']})
        logger.info(f"All liabilities deleted successfully for user: {current_user.get('user_id')}")
        return {"message": "All liabilities deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting all liabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
