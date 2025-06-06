import pytest
from fastapi import HTTPException
from app.auth.service import cognito_client
from app.tests.model_fixtures import mock_user_signup, mock_user_confirm, mock_user_signin
from app.main import app
from app.user import utils as user_utils


"""
Sign up User Tests
"""

@pytest.mark.asyncio
async def test_signup_success(async_test_client, mocker, mock_user_signup):
    mocker.patch("app.auth.service.cognito_client.sign_up", return_value={"UserConfirmed": False})
    mocker.patch("app.auth.service.cognito_client.list_users", return_value={"Users": []})

    response = await async_test_client.post("/auth/signup", json=mock_user_signup.model_dump())

    assert response.status_code == 200
    assert response.json() == {"message": "User signed up successfully."}

@pytest.mark.asyncio
async def test_signup_user_already_exists(async_test_client, mocker, mock_user_signup):
    """
    Test user signup when the user already exists.
    """
    mocker.patch("app.auth.service.cognito_client.list_users", return_value={"Users": [{"Username": "testuser"}]})
    
    response = await async_test_client.post("/auth/signup", json=mock_user_signup.model_dump())

    assert response.status_code == 400
    assert response.json() == {"detail": "User with this email already exists."}


"""
Confirm User Tests
"""

@pytest.mark.asyncio
async def test_confirm_user_success(async_test_client, mocker, mock_user_confirm):
    """
    Test successful user confirmation.
    """
    mocker.patch("app.auth.service.auth_utils.generate_secret_hash", return_value="fake_hash")
    mocker.patch("app.auth.service.cognito_client.confirm_sign_up", return_value={"message": "User confirmed successfully."})
    
    response = await async_test_client.post("/auth/confirm", json=mock_user_confirm.model_dump())

    assert response.status_code == 200
    assert response.json() == {"message": "User confirmed successfully."}

@pytest.mark.asyncio
async def test_confirm_user_failure(async_test_client, mocker, mock_user_confirm):
    """
    Test user confirmation failure due to invalid confirmation code.
    """
    mocker.patch("app.auth.service.auth_utils.generate_secret_hash", return_value="fake_hash")
    mocker.patch("app.auth.service.cognito_client.confirm_sign_up", side_effect=Exception("Invalid confirmation code"))
    
    response = await async_test_client.post("/auth/confirm", json=mock_user_confirm.model_dump())

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid confirmation code"}


"""
Sign in User Tests
"""

@pytest.mark.asyncio
async def test_signin_success(async_test_client, mocker, mock_user_signup):
    """
    Test successful user sign-in
    """
    mocker.patch("app.auth.service.auth_utils.generate_secret_hash", return_value="fake_hash")
    mocker.patch("app.auth.service.cognito_client.initiate_auth", return_value={
        "AuthenticationResult": {
            "IdToken": "fake_id_token",
            "AccessToken": "fake_access_token",
            "RefreshToken": "fake_refresh_token"
        }
    })

    response = await async_test_client.post("/auth/signin", json=mock_user_signup.model_dump())

    assert response.status_code == 200
    assert response.json() == {"message": "User signed in successfully."}

@pytest.mark.asyncio
async def test_signin_invalid_credentials(async_test_client, mocker, mock_user_signin):
    """
    Test user sign-in with invalid credentials.
    """
    mocker.patch("app.auth.service.auth_utils.generate_secret_hash", return_value="fake_hash")
    mocker.patch("app.auth.service.cognito_client.initiate_auth", side_effect=cognito_client.exceptions.NotAuthorizedException(
        {
            "Error": {
                "Code": "NotAuthorizedException",
                "Message": "Incorrect username or password"}
        },
        operation_name="InitiateAuth"))

    response = await async_test_client.post("/auth/signin", json=mock_user_signin.model_dump())

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}


"""
Logout User Tests
"""

@pytest.mark.asyncio
async def test_logout_success(async_test_client, mocker):
    """
    Test successful user logout.
    """
    mocker.patch("app.auth.service.cognito_client.global_sign_out", return_value={"message": "User logged out successfully."})
    
    async def get_fake_current_user_id():
        return {
            "username": "testuser",
            "access_token": "fake_access_token"
        }
    
    app.dependency_overrides[user_utils.get_current_user_id] = get_fake_current_user_id

    response = await async_test_client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "User successfully logged out."}

@pytest.mark.asyncio
async def test_logout_failure(async_test_client, mocker):
    """
    Test user logout failure due to missing access token
    """
    async def get_fake_current_user_id():
        raise HTTPException(status_code=400, detail="Access token is missing")

    app.dependency_overrides[user_utils.get_current_user_id] = get_fake_current_user_id

    response = await async_test_client.post("/auth/logout")

    assert response.status_code == 400
    assert response.json() == {"detail": "Access token is missing"}
