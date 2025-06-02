from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime


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
    identity_id: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None


class AssetBase(BaseModel):
    category: str
    title: str
    asset_value: float

class Asset(AssetBase):
    asset_id: UUID
    created_at: datetime 

class LiabilityBase(BaseModel):
    category: str
    title: str
    liability_value: float

class Liability(LiabilityBase):
    liability_id: UUID
    created_at: datetime