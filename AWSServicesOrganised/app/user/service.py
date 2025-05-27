import boto3
import botocore
import uuid

from fastapi import HTTPException, Depends, UploadFile, File

from app.config import CLIENT_ID, REGION, USERPOOL_ID, S3_BUCKET_NAME, S3_REGION, S3_BASE_URL, S3_PROFILE_PIC_FOLDER
from app.user import utils as user_utils
from app.models import UserProfile

cognito_client = boto3.client("cognito-idp", region_name=REGION)
s3_client = boto3.client("s3", region_name=S3_REGION)
dynamodb_client = boto3.resource("dynamodb", region_name=REGION)


def upload_pic(
    file: UploadFile = File(...),
    current_user: dict = Depends(user_utils.get_current_user)    
    ):
    """
    Uploads a profile picture to S3 and returns the S3 key and public URL.
    """
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
        
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{S3_PROFILE_PIC_FOLDER}/{current_user['sub']}/profile_pic.{file_extension}"
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
    current_user: dict = Depends(user_utils.get_current_user)
    ):
    """
    Retrieves the profile picture URL from S3 for the current user.
    """
    try:
        key = f"profile_pic/{current_user['sub']}/profile_pic.jpeg"

        try:
            s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
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
        return {"profile_pic_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


def update_profile_details(
    profile: UserProfile,
    current_user: dict = Depends(user_utils.get_current_user)
    ):
    """
    Updates the user profile details in DynamoDB.
    """
    try:
        user_sub = current_user['sub']
        username = current_user['username']

        profile_pic_key = f"{S3_PROFILE_PIC_FOLDER}/{user_sub}/profile_pic.jpeg"
        S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"        
        profile_pic_url = f"{S3_BASE_URL}/{profile_pic_key}"

        item = {
            "userName": username,
            "sub": user_sub,
            "name": profile.name,
            "height": profile.height,
            "gender": profile.gender,
            "dob": profile.dob,
            "profile_pic_key":profile_pic_key,
            "profile_pic_url": profile_pic_url,
        }
        
        table = dynamodb_client.Table("userProfiles")
        table.put_item(Item=item)
        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


def get_profile_details(
    current_user: dict = Depends(user_utils.get_current_user)
    ):
    """
    Retrieves the user profile details from DynamoDB.
    """
    try:
        username = current_user['username']
        table = dynamodb_client.Table("userProfiles")
        response = table.get_item(Key={"userName": username})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="User profile not found")
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

