import boto3
import uuid
import datetime
from fastapi import Depends, HTTPException
from decimal import Decimal

from app.models import LiabilityBase
from app.user import utils as user_utils
from app.config import REGION, DynamoDB_LIABILITY_DETAILS_TABLE


def create_liability(
        liability: LiabilityBase,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
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
        return {"Liability created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def list_liabilities_per_user(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        response = table.query(
            IndexName="UserSubIndex",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(current_user['username'])
        )
        return response.get('Items', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_liability_by_id(
        liability_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        response = table.get_item(
            Key={"liability_id": liability_id}
        )
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="Liability not found")
        if item.get("sub") != current_user["sub"]:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_liability(
        liability_id: str,
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        table.delete_item(Key={"liability_id": liability_id})
        return {"message": "Liability deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_all_liabilities(
        current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    try:
        session, _ = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_LIABILITY_DETAILS_TABLE)

        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(current_user['username'])
        )
        for item in response.get('Items', []):
            table.delete_item(Key={"liability_id": item['liability_id']})
        return {"message": "All liabilities deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
