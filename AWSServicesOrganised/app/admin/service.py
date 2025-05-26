import boto3
from fastapi import HTTPException, Depends
from app.config import USERPOOL_ID, REGION
from app.user import utils as user_utils

cognito_client = boto3.client('cognito-idp', region_name=REGION)

def get_all_users_cognito_userpool() -> dict:

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

