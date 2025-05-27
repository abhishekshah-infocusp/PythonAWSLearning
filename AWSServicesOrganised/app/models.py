from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserNameModel(BaseModel):
    username: str


class UserSignUp(UserNameModel):
    password: str
    email: EmailStr


class UserSignIn(UserNameModel):
    password: str


class UserConfirm(UserNameModel):
    confirmation_code: str


class UserProfile(UserNameModel):
    username: str = Field(..., alias="userName")
    name: Optional[str] = None
    height: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None


class UserProfileFull(UserProfile):
    sub: str
    name: str
    profile_pic_key: Optional[str]
    profile_pic_url: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None
