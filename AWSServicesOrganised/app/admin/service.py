import boto3

from fastapi import HTTPException, Depends, Request
from botocore.exceptions import ClientError

from app.config import USERPOOL_ID, REGION
from app.user import utils as user_utils
from app.admin import utils as admin_utils

def handle_cognito_error(e: ClientError):
    """
    Handles specific Cognito client errors and raises appropriate HTTP exceptions.
    """
    error_code = e.response.get("Error", {}).get("Code")

    if error_code == "InvalidParameterException":
        raise HTTPException(status_code=400, detail="Some input is invalid. Please check your details and try again.")
    elif error_code == "ResourceNotFoundException":
        raise HTTPException(status_code=400, detail="Requested resource was not found.")
    elif error_code == "TooManyRequestsException":
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in a moment.")
    elif error_code == "NotAuthorizedException":
        raise HTTPException(status_code=401, detail="You are not authorized to perform this action.")
    elif error_code == "InternalErrorException":
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")
    else:
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")


def get_all_users_cognito_userpool(request: Request) -> dict:
    """
    Retrieves all users from the Cognito User Pool.
    """
    try:
        cognito_client = admin_utils.get_admin_cognito_client(request)
        response = cognito_client.list_users(
            UserPoolId=USERPOOL_ID,
        )
        return response
    except ClientError as e:
        handle_cognito_error(e)


def get_user_by_email(
    email: str,
    request: Request
    ):
    """
    Retrieves a user from the Cognito User Pool by their email address.
    """
    try:
        cognito_client = admin_utils.get_admin_cognito_client(request)
        response = cognito_client.list_users(
            UserPoolId=USERPOOL_ID,
            Filter=f'email = "{email}"'
        )
        if not response['Users']:
            raise HTTPException(status_code=404, detail="User not found.")
        return response['Users'][0]
    except ClientError as e:
        handle_cognito_error(e)


def get_user_by_username(
    username: str,
    request: Request
    ):
    """
    Retrieves a user from the Cognito User Pool by their username.
    """
    try:
        cognito_client = admin_utils.get_admin_cognito_client(request)
        response = cognito_client.list_users(
            UserPoolId=USERPOOL_ID,
            Filter=f'username = "{username}"'
        )
        if not response['Users']:
            raise HTTPException(status_code=404, detail="User not found.")
        return response['Users'][0]
    except ClientError as e:
        handle_cognito_error(e)

