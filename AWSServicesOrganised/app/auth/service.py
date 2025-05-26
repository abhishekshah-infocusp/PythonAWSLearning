import boto3
import jwt
import httpx

from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.models import User
from app.auth.utils import generate_secret_hash
from app.config import CLIENT_ID, REGION, USERPOOL_ID
from jwt.exceptions import ExpiredSignatureError, PyJWTError


cognito_client = boto3.client("cognito-idp", region_name=REGION)

async def get_cognito_public_keys():
    """
    Fetches the public keys from Cognito for JWT verification.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}/.well-known/jwks.json")
            response.raise_for_status()
            return response.json()['keys']
    except httpx.HTTPError as e:
        print(f"Error fetching Cognito JWKS: {e}")
        return None


async def verify_token(token: str) -> dict:
    keys = await get_cognito_public_keys()
    if not keys:
        raise HTTPException(status_code=401, detail="Failed to retrieve Cognito public keys.")

    try:
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        key = next((k for k in keys if k['kid'] == kid), None)
        if key is None:
            raise HTTPException(status_code=401, detail="Invalid token: Key ID not found.")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=CLIENT_ID,
            issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}"
        )

        return {"username": payload.get('username'), "sub": payload.get('sub')}

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        print(f"Error verifying token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token.")


def handle_client_error(e):
    error_code = e.response.get("Error", {}).get("Code")
    if error_code == "UsernameExistsException":
        raise HTTPException(status_code=400, detail="Username already exists.")
    elif error_code == "InvalidPasswordException":
        raise HTTPException(status_code=400, detail="Password does not meet policy requirements.")
    elif error_code == "InvalidParameterException":
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e.response['Error']['Message']}")
    else:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {error_code}")


async def signup_user(user: User) -> dict:
    try:
        secret_hash = await generate_secret_hash(user.username)
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

async def confirm_user(user: User) -> dict:
    try:
        secret_hash = await generate_secret_hash(user.username)
        return cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            ConfirmationCode=user.confirmation_code,
            SecretHash=secret_hash,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def signin_user(user: User) -> dict:
    try:
        secret_hash = await generate_secret_hash(user.username)
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
    try:
        cognito_client.global_sign_out(AccessToken=token)
        return {"message": "Successfully logged out"}
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
