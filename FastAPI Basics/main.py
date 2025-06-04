from fastapi import FastAPI, Path, Body
from typing import List, Optional
from pydantic import BaseModel, field_validator, Field


app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False


class ItemRequest(BaseModel):
    q: Optional[str] = Field("Hello World!", min_length=3, max_length=50)
    size: Optional[int] = Field(None, ge=0, le=100)
    tags: List[str] = Field(..., min_length=1, max_length=5)

    @field_validator("tags")
    def validate_tags(cls, tags_list):
        for tag in tags_list:
            if len(tag) < 2:
                raise ValueError("Tag must be at least 2 characters long")
        return tags_list

"""
Handlers for the FastAPI application
"""
@app.get("/")
async def read_main():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    return {
        "name": item.name,
        "price": item.price,
        "is_offer": item.is_offer
    }

@app.post("/items/{item_id}")
async def read_item(item_id: int = Path(..., gt=0), body: ItemRequest = Body(...)):
    return {"item_id": item_id, **body.dict()}








# from typing import Annotated, Union
# from pydantic import BaseModel, EmailStr
# from fastapi import Cookie, FastAPI, Header, status, Form, File, UploadFile

# app = FastAPI()

# Cookies
# @app.get("/items/")
# async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
#     return {"ads_id": ads_id}


# Getting the header parameters
# @app.get("/items/")
# async def read_items(
#     user_agent: Annotated[str | None, Header()] = None,
#     host: Annotated[str | None, Header()] = None,
#     connection: Annotated[str | None, Header()] = None
#     ):
#     return {"User-Agent": user_agent, "Host": host, "Connection": connection}


# class UserIn(BaseModel):
#     username: str
#     password: str
#     email: EmailStr
#     full_name: str | None = None


# class UserOut(BaseModel):
#     username: str
#     email: EmailStr
#     full_name: str | None = None


# class UserInDB(BaseModel):
#     username: str
#     hashed_password: str
#     email: EmailStr
#     full_name: str | None = None


# def fake_password_hasher(raw_password: str):
#     return "supersecret" + raw_password


# def fake_save_user(user_in: UserIn):
#     hashed_password = fake_password_hasher(user_in.password)
#     user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
#     print("User saved! ..not really")
#     return user_in_db


# @app.post("/user/", response_model=UserOut)
# async def create_user(user_in: UserIn):
#     user_saved = fake_save_user(user_in)
#     return user_saved


# app = FastAPI()


# class UserBase(BaseModel):
#     username: str
#     email: EmailStr
#     full_name: str | None = None


# class UserIn(UserBase):
#     password: str


# class UserOut(UserBase):
#     pass


# class UserInDB(UserBase):
#     hashed_password: str


# def fake_password_hasher(raw_password: str):
#     return "supersecret" + raw_password


# def fake_save_user(user_in: UserIn):
#     hashed_password = fake_password_hasher(user_in.password)
#     user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
#     print("User saved! ..not really")
#     return user_in_db


# @app.post("/user/", response_model=UserOut)
# async def create_user(user_in: UserIn):
#     user_saved = fake_save_user(user_in)
#     return user_saved

# class BaseItem(BaseModel):
#     description: str
#     type: str


# class CarItem(BaseItem):
#     type: str = "car"


# class PlaneItem(BaseItem):
#     type: str = "plane"
#     size: int


# items = {
#     "item1": {"description": "All my friends drive a low rider", "type": "car"},
#     "item2": {
#         "description": "Music is my aeroplane, it's my aeroplane",
#         "type": "plane",
#         "size": 5,
#     },
# }

# @app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
# async def read_item(item_id: str):
#     return items[item_id]

# @app.post("/login/")
# async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
#     return {"username": username}

# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     return {"file_size": len(file)}

# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile | None = None):
#     if not file:
#         return {"message": "No upload file sent"}
#     return {"filename": file.filename}

# @app.post("/uploadfiles/")
# async def create_upload_files(files: list[UploadFile]):
#     return {"filenames": [file.filename for file in files]}

# @app.post("/files2/")
# async def create_file (
#     file: Annotated[bytes, File()],
#     fileb: Annotated[UploadFile, File()],
#     token: Annotated[str, Form()]
#     ):
#     return {
#         "file_size": len(file),
#         "token": token,
#         "fileb_content_type": fileb,
#     }


# Testing FastAPI with Pytest
