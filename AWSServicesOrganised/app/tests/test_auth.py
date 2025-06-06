import pytest


@pytest.mark.asyncio
async def test_signup_success(async_test_client, mocker):
    """
    Test successful user signup.
    """
    mocker.patch("app.auth.service.cognito_client.sign_up", return_value={"UserConfirmed": False})
    mocker.patch("app.auth.service.cognito_client.list_users", return_value={"Users": []})

    response = await async_test_client.post("/auth/signup", json={
        "username": "testuser",
        "password": "test@123",
        "email": "test@gmail.com"
    })

    assert response.status_code == 200
    assert response.json() == {"UserConfirmed": False}


@pytest.mark.asyncio
async def test_signup_user_already_exists(async_test_client, mocker):
    """
    Test user signup when the user already exists.
    """
    mocker.patch("app.auth.service.cognito_client.list_users", return_value={"Users": [{"Username": "testuser"}]})
    
    response = await async_test_client.post("/auth/signup", json={
        "username": "testuser",
        "password": "test@123",
        "email": "test@gmail.com"
    })

    assert response.status_code == 400
    assert response.json() == {"detail": "User with this email already exists."}


