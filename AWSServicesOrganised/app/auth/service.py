import boto3
import jwt
import httpx
import logging

from botocore.exceptions import ClientError
from fastapi import HTTPException, Response, Depends
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from app.models import UserSignUp, UserConfirm, UserSignIn, Token
from app.auth import utils as auth_utils
from app.config import CLIENT_ID, REGION, USERPOOL_ID
from app.user import utils as user_utils


logger = logging.getLogger(__name__)
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
        logger.info(f"Signing up user: {user.username}")

        # Check if the user already exists
        existing_users = cognito_client.list_users(
            UserPoolId=USERPOOL_ID,
            Filter=f'email = "{user.email}"'
        )
        if existing_users['Users']:
            logger.warning(f"User with email {user.email} already exists!")
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        secret_hash = await auth_utils.generate_secret_hash(user.username)
        logger.info(f"Generated secret hash for user: {user.username}")
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            Password=user.password,
            SecretHash=secret_hash,
            UserAttributes=[
                {"Name": "email", "Value": user.email},
                {"Name": "name", "Value": user.username},
            ],
        )
        return {"message": "User signed up successfully."}
    except ClientError as e:
        logger.error(f"Error signing up user {user.username}: {str(e)}")
        handle_client_error(e)


async def confirm_user(user: UserConfirm) -> dict:
    """
    Confirms a user's sign-up in the Cognito User Pool.
    """
    try:
        logger.info(f"Confirming user: {user.username}")
        secret_hash = await auth_utils.generate_secret_hash(user.username)
        return cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            ConfirmationCode=user.confirmation_code,
            SecretHash=secret_hash,
        )
        logger.info(f"User {user.username} confirmed successfully.")
        return {"message": "User confirmed successfully."}
    except Exception as e:
        logger.error(f"Error confirming user {user.username}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def signin_user(user: UserSignIn, res: Response) -> dict:
    """
    Signs in a user and returns authentication tokens.
    """
    try:
        logger.info(f"Signing in user: {user.username}")
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
        res.set_cookie(
            key="id_token",
            value=response['AuthenticationResult']['IdToken'],
            httponly=False,
            secure=False
        )
        res.set_cookie(
            key="access_token",
            value=response['AuthenticationResult']['AccessToken'],
            httponly=False,
            secure=False
        )
        res.set_cookie(
            key="refresh_token",
            value=response['AuthenticationResult']['RefreshToken'],
            httponly=False,
            secure=False
        )
        logger.info(f"User {user.username} signed in successfully.")
        return {"message": "User signed in successfully."}
    except cognito_client.exceptions.NotAuthorizedException:
        logger.error(f"Incorrect username or password for user: {user.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    except Exception as e:
        logger.error(f"Error signing in user {user.username}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def logout_user(
    current_user: dict = Depends(user_utils.get_current_user_id),
) -> dict:
    """
    Logs out a user.
    """
    try:
        logger.info(f"Logging out user: {current_user['username']}")
        cognito_client.global_sign_out(accessToken=current_user['access_token'])
        logger.info(f"User {current_user['username']} logged out successfully.")
        return {"message": "User successfully logged out."}
    except cognito_client.exceptions.NotAuthorizedException:
        logger.error(f"User {current_user['username']} is not authorized to log out.")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        logger.error(f"Error logging out user {current_user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
