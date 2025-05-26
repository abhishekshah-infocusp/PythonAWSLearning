import boto3
import botocore
import uuid
from fastapi import HTTPException, Depends, UploadFile, File
from app.config import CLIENT_ID, REGION, USERPOOL_ID, S3_BUCKET_NAME, S3_REGION, S3_BASE_URL, S3_PROFILE_PIC_FOLDER
from app.users import utils as user_utils

cognito_client = boto3.client("cognito-idp", region_name=S3_REGION)
s3_client = boto3.client("s3", region_name=S3_REGION)

def list_users() -> dict:
    try:
        response = cognito_client.list_users(
            UserPoolId=USERPOOL_ID,
        )
        return response
    except cognito_client.exceptions.InvalidParameterException as e:
        raise HTTPException(status_code=400, detail="Invalid Parameters!")
    except cognito_client.exceptions.ResourceNotFoundException as e:
        raise HTTPException(status_code=400, detail="Resource Not found!")
    except cognito_client.exceptions.TooManyRequestsException as e:
        raise HTTPException(status_code=400, detail="Too Many Requests!")
    except cognito_client.exceptions.NotAuthorizedException as e:
        raise HTTPException(status_code=400, detail="Not authorized!")
    except cognito_client.exceptions.InternalErrorException as e:
        raise HTTPException(status_code=400, detail="Internal Eror!")

def upload_pic(
    file: UploadFile = File(...),
    current_user: dict = Depends(user_utils.get_current_user)    
):
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

        s3_key = "Not yet implemented"
        return {
            "message": "Profile picture uploaded successfully", 
            "s3_key": s3_key,
            "url": file_public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 

def get_profile_picture (
    current_user: dict = Depends(user_utils.get_current_user)
):
    try:
        key = f"profile_pic/{current_user['sub']}/profile_pic.jpeg"
        # key = f"profile_pic/703c59cc-e0b1-70f6-8ca9-f6caf8ce8a5a/profile_pic.jpeg"

        print(f"Fetching profile picture for user: {current_user}")
        # To check if it exists
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