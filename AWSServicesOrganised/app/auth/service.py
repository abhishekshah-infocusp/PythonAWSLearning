import boto3
import jwt
import httpx

from botocore.exceptions import ClientError
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from app.models import UserSignUp, UserConfirm, UserSignIn, Token
from app.auth import utils as auth_utils
from app.config import CLIENT_ID, REGION, USERPOOL_ID

cognito_client = boto3.client("cognito-idp", region_name=REGION)

def handle_client_error(e: ClientError):
    """
    Handles specific Cognito client errors and raises appropriate HTTP exceptions.
    """

    error_code = e.response.get("Error", {}).get("Code")
    if error_code == "UsernameExistsException":
        raise HTTPException(status_code=400, detail="This username is already taken.")
    elif error_code == "InvalidPasswordException":
        raise HTTPException(status_code=400, detail="Password does not meet policy requirements.")
    elif error_code == "InvalidParameterException":
        raise HTTPException(status_code=400, detail=f"Some input is invalid. Please check your details and try again.")
    else:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. Please try again later.")


async def signup_user(user: UserSignUp) -> dict:
    """
    Signs up a new user in the Cognito User Pool.
    """
    try:
        # Check if the user already exists
        existing_users = cognito_client.list_users(
            UserPoolId=USERPOOL_ID,
            Filter=f'email = "{user.email}"'
        )
        print(f"Existing users: {existing_users}")
        if existing_users['Users']:
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        secret_hash = await auth_utils.generate_secret_hash(user.username)
        return cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            Password=user.password,
            SecretHash=secret_hash,
            UserAttributes=[
                {"Name": "email", "Value": user.email},
                {"Name": "name", "Value": user.username},
            ],
        )
    except ClientError as e:
        handle_client_error(e)


async def confirm_user(user: UserConfirm) -> dict:
    """
    Confirms a user's sign-up in the Cognito User Pool.
    """
    try:
        secret_hash = await auth_utils.generate_secret_hash(user.username)
        return cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            ConfirmationCode=user.confirmation_code,
            SecretHash=secret_hash,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def signin_user(user: UserSignIn) -> dict:
    """
    Signs in a user and returns authentication tokens.
    """
    try:
        secret_hash = await auth_utils.generate_secret_hash(user.username)
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=CLIENT_ID,
            AuthParameters={
                'USERNAME': user.username,
                'PASSWORD': user.password,
                'SECRET_HASH': secret_hash
            },
        )
        return {
            "access_token": response['AuthenticationResult']['AccessToken'],
            "id_token": response['AuthenticationResult']['IdToken'],
            "refresh_token": response['AuthenticationResult']['RefreshToken'],
            "expires_in": response['AuthenticationResult']['ExpiresIn'],
            "token_type": response['AuthenticationResult']['TokenType'],
        }
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def logout_user(token: str) -> dict:
    """
    Logs out a user.
    """
    try:
        cognito_client.global_sign_out(AccessToken=token)
        return {"message": "Successfully logged out"}
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
