import boto3

from fastapi import Request, HTTPException

from app.config import ADMIN_IDENTITYPOOL_ID, USERPOOL_ID, REGION


def get_admin_cognito_client(request: Request):

    id_token = request.cookies.get("id_token")

    if not id_token:
        raise HTTPException(status_code=401, detail="Authentication token missing.")

    identity_client = boto3.client('cognito-identity', region_name=REGION)

    USER_POOL_PROVIDER = f"cognito-idp.{REGION}.amazonaws.com/{USERPOOL_ID}"

    # get IdentityId for the user
    identity_response = identity_client.get_id(
        IdentityPoolId=ADMIN_IDENTITYPOOL_ID,
        Logins={
            USER_POOL_PROVIDER: id_token
        }
    )

    identity_id = identity_response['IdentityId']

    # get temperary credentials for the identity
    creds_response = identity_client.get_credentials_for_identity(
        IdentityId=identity_id,
        Logins={
            USER_POOL_PROVIDER: id_token
        }
    )

    creds = creds_response['Credentials']

    # Use temporary credentials to create Cognito client
    cognito_client = boto3.client(
        'cognito-idp',
        region_name=REGION,
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretKey'],
        aws_session_token=creds['SessionToken'],
    )

    return cognito_client
