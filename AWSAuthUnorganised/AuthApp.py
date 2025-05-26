import base64
import hashlib
import hmac
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import boto3
from typing import Optional
from botocore.exceptions import ClientError

import uvicorn


app = FastAPI()
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REGION = os.getenv("REGION")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

cognito_client = boto3.client('cognito-idp', region_name = REGION)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    confirmation_code: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


async def generate_secret_hash(username: str, client_id: str, client_secret: str) -> str:
    message = username + client_id
    digest = hmac.new(key=client_secret.encode("utf-8"), msg=message.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

@app.post("/signup", response_model= dict)
async def signup(user: User):
    try:
        secretHash = await generate_secret_hash(user.username, CLIENT_ID, CLIENT_SECRET)
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            Password=user.password,
            SecretHash = secretHash,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user.email,
                },
                {
                    'Name': 'name',
                    'Value': user.username
                }
            ]
        )
        return response
    
    except ClientError as e: 
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == 'UsernameExistsException':
            raise HTTPException(status_code=400, detail="Username already exists.")
        elif error_code == 'InvalidPasswordException':
            raise HTTPException(status_code=400, detail="Password does not meet policy requirements.")
        elif error_code == 'InvalidParameterException':
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {e.response['Error']['Message']}")
        else:
            print(f"Cognito sign_up error: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {error_code}")
    
    except Exception as e:
        # Log the full error for debugging
        print(f"General error in signup: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")



@app.post("/confirm", response_model=dict)
async def confirm(user: User):
    try:
        secretHash = await generate_secret_hash(user.username, CLIENT_ID, CLIENT_SECRET)

        response = cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=user.username,
            ConfirmationCode=user.confirmation_code,
            SecretHash = secretHash,            
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/signin", response_model=Token)
async def signin(user: User):
    try:
        secretHash = await generate_secret_hash(user.username, CLIENT_ID, CLIENT_SECRET)
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId = CLIENT_ID,
            AuthParameters={
                'USERNAME': user.username,
                'PASSWORD': user.password,
                'SECRET_HASH': secretHash
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
    
@app.post("/logout", response_model=dict)
def logout(token: str = Depends(oauth2_scheme)):
    try:
        response = cognito_client.global_sign_out(
            AccessToken=token
        )
        return {"message": "Successfully logged out"}
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    uvicorn.run("AuthApp:app", host="0.0.0.0", port=3000, reload=True)

