from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    confirmation_code: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserProfile(BaseModel):
    username: str
    height: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None

class UserProfileFull(BaseModel):
    userName: str
    sub: str
    name: str
    height: Optional[str]
    gender: Optional[str]
    dob: Optional[str]
    profile_pic_key: Optional[str]
    profile_pic_url: Optional[str]
