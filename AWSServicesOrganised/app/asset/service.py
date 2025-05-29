import boto3
import uuid
import datetime

from fastapi import Depends
from decimal import Decimal

from app.models import AssetBase
from app.user import utils as user_utils
from app.config import REGION, DynamoDB_ASSET_DETAILS_TABLE

dynamodb_client = boto3.resource("dynamodb", region_name=REGION)

def create_asset(
        asset: AssetBase,
        username: str
    ):
    asset_id = str(uuid.uuid4()) 
    item = {
        "asset_id": asset_id,
        "username": username,
        "category": asset.category,
        "title": asset.title,
        "asset_value": Decimal(str(asset.asset_value)),
        "created_at": datetime.datetime.utcnow().isoformat(),
        "doc_paths": []
    }

    print(item)

    table = dynamodb_client.Table(DynamoDB_ASSET_DETAILS_TABLE)

    print(table)
    table.put_item(Item=item)

    return {"Asset created successfully"}

        # user_sub = current_user['sub']
        # username = current_user['username']

        # profile_pic_key = f"{S3_PROFILE_PIC_FOLDER}/{user_sub}/profile_pic.jpeg"
        # S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"        
        # profile_pic_url = f"{S3_BASE_URL}/{profile_pic_key}"

        # item = {
        #     "userName": username,
        #     "sub": user_sub,
        #     "name": profile.name,
        #     "height": profile.height,
        #     "gender": profile.gender,
        #     "dob": profile.dob,
        #     "profile_pic_key":profile_pic_key,
        #     "profile_pic_url": profile_pic_url,
        # }
        
        # table = dynamodb_client.Table(DynamoDB_USER_DETAILS_TABLE)
        # table.put_item(Item=item)
        # return {"message": "Profile updated successfully"}
