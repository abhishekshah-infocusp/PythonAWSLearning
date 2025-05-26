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
