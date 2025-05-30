import requests
import boto3

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.auth import service as auth_service
from app.config import REGION, USERPOOL_ID, CLIENT_ID, IDENTITYPOOL_ID

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_jwks = None
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}/.well-known/jwks.json"


def get_jwks() -> dict:
    global _jwks
    if not _jwks:
        _jwks = requests.get(JWKS_URL).json()
    return _jwks


def get_current_user_id(request: Request) -> dict:
    token = request.cookies.get("id_token") or request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing in cookies or Authorization header")
    try:
        # Decode as usual (assumes ID token passed in Authorization header)
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)

        key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}"
        )

        if payload.get("token_use") != "id":
            raise HTTPException(status_code=401, detail="Token must be an ID token")

        if 'cognito:groups' in payload:
            cognito_groups = payload['cognito:groups']
        else:
            cognito_groups = None

        return {
            "username": payload.get("cognito:username"),
            "sub": payload.get("sub"),
            "scope": payload.get("scope"),
            "cognito:groups": cognito_groups,
            "id_token": token
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")


def require_admin(current_user: dict = Depends(get_current_user_id)):
    groups = current_user.get('cognito:groups') or []
    if groups is None or 'admin' not in groups:
        raise HTTPException(status_code=403, detail="You are not Admin user, you do not have permission to access this resource.")
    return current_user

def get_identity_credentials_with_userpool_token(user_pool_token: str):
    cognito_identity_client = boto3.client("cognito-identity", region_name=REGION)
    USER_POOL_PROVIDER = f"cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}"

    identity_response = cognito_identity_client.get_id(
        IdentityPoolId=IDENTITYPOOL_ID,
        Logins={
            USER_POOL_PROVIDER: user_pool_token
        }
    )
    identity_id = identity_response['IdentityId']

    credentials_response = cognito_identity_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={
            USER_POOL_PROVIDER: user_pool_token
        }
    )
    creds = credentials_response['Credentials']

    session = boto3.Session(
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretKey'],
        aws_session_token=creds['SessionToken']
    )

    return session, identity_id

