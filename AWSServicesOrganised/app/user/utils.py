import requests

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.auth import service as auth_service
from app.config import REGION, USERPOOL_ID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_jwks = None
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}/.well-known/jwks.json"


def get_jwks():
    global _jwks
    if not _jwks:
        _jwks = requests.get(JWKS_URL).json()
    return _jwks


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)

        key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=None,  # No "aud" in access tokens
            issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}"
        )

        if payload.get("token_use") != "access":
            raise HTTPException(status_code=401, detail="Invalid token use")

        if 'cognito:groups' in payload:
            cognito_groups = payload['cognito:groups']
        else:
            cognito_groups = None

        return {
            "username": payload.get("username"), 
            "sub": payload.get("sub"),
            "scope": payload.get("scope"),
            "cognito:groups": cognito_groups
        }

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")


def require_admin(current_user: dict = Depends(get_current_user)):
    groups = current_user.get('cognito:groups') or []
    if groups is None or 'admin' not in groups:
        raise HTTPException(
            status_code=403,
            detail="You are not Admin user, you do not have permission to access this resource."
        )
    return current_user

