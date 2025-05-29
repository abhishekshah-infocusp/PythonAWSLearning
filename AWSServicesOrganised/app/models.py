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


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None


class AssetBase(BaseModel):
    username: str
    category: str
    title: str
    asset_value: float
    doc_paths: Optional[List[str]] = Field(
        default_factory=list,
        description="List of s3 document paths related to the assets"
    )

class Asset(AssetBase):
    asset_id: UUID
    created_at: datetime 
