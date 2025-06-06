import pytest

from app.models import UserSignUp, UserConfirm, UserSignIn

@pytest.fixture
def mock_user_signup():
    return UserSignUp(
        username="testuser",
        password="test@123",
        email="test@gmail.com")

@pytest.fixture
def mock_user_confirm():
    return UserConfirm(
        username="testuser",
        confirmation_code="123456")

@pytest.fixture
def mock_user_signin():
    return UserSignIn(
        username="testuser",
        password="test@123")
