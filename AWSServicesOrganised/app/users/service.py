import boto3
from fastapi import HTTPException, Depends, UploadFile, File
from app.config import CLIENT_ID, REGION, USERPOOL_ID
from app.users import utils as user_utils

cognito_client = boto3.client("cognito-idp", region_name=REGION)

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
        # Logic to add image to s3 
        s3_key = "Not yet implemented"
        return {"message": "Profile picture uploaded successfully", "s3_key": s3_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    