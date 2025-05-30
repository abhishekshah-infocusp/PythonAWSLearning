import boto3
import botocore
import uuid

from boto3.session import Session
from fastapi import HTTPException, Depends, UploadFile, File

from app.config import CLIENT_ID, REGION, USERPOOL_ID, S3_BUCKET_NAME, S3_REGION, S3_BASE_URL, S3_PROFILE_PIC_FOLDER, DynamoDB_USER_DETAILS_TABLE, AWS_ACCOUNT_ID, IDENTITYPOOL_ID
from app.user import utils as user_utils
from app.models import UserProfile

def upload_pic(
    file: UploadFile = File(...),
    current_user: dict = Depends(user_utils.get_current_user_id)    
    ):
    """
    Uploads a profile picture to S3 and returns the S3 key and public URL.
    """
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
        
        session,identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])        
        s3_client = session.client("s3", region_name=S3_REGION)

        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{S3_PROFILE_PIC_FOLDER}/{identity_id}/profile_pic.{file_extension}"
        S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"

        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            unique_filename,
        )
        
        file_public_url = f"{S3_BASE_URL}/{unique_filename}"

        return {
            "message": "Profile picture uploaded successfully", 
            "s3_key": unique_filename,
            "url": file_public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 

def get_profile_picture (
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Retrieves the profile picture URL from S3 for the current user.
    """
    try:
        key = f"profile_pic/eu-north-1:35185232-0d9f-c39d-baf9-59ace0bb1539/profile_pic.jpeg"

        try:
            session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
            s3_client = session.client("s3", region_name=S3_REGION)
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ("404", "403"):
                raise HTTPException(status_code=404, detail="Profile picture does not exist or access to profile picture forbidden.")
            else:
                raise HTTPException(status_code=400, detail=str(e))

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
            ExpiresIn=3600  # 1 hour
        )
        return {"message": "Profile picture fetched succesfully", "profile_pic_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


def update_profile_details(
    profile: UserProfile,
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Updates the user profile details in DynamoDB.
    """
    try:
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_USER_DETAILS_TABLE)

        profile_pic_key = f"{S3_PROFILE_PIC_FOLDER}/{identity_id}/profile_pic.jpeg"
        S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"        
        profile_pic_url = f"{S3_BASE_URL}/{profile_pic_key}"

        item = {
            "userName": current_user['username'],
            "sub": current_user['sub'],
            "name": profile.name,
            "height": profile.height,
            "gender": profile.gender,
            "dob": profile.dob,
            "profile_pic_key":profile_pic_key,
            "profile_pic_url": profile_pic_url,
            "identity_id": identity_id
        }

        table.put_item(Item=item)
        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


def get_profile_details(
    current_user: dict = Depends(user_utils.get_current_user_id)
    ):
    """
    Retrieves the user profile details from DynamoDB.
    """
    try:
        username = current_user['username']
        session, identity_id = user_utils.get_identity_credentials_with_userpool_token(current_user['id_token'])
        dynamodb = session.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(DynamoDB_USER_DETAILS_TABLE)
        response = table.get_item(Key={"userName": username})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="User profile not found")
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

