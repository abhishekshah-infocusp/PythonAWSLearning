import os

from fastapi import FastAPI
from dotenv import load_dotenv

from app.auth.handlers import router as auth_router
from app.user.handlers import router as user_router

# Run the App
app = FastAPI()

# App configuraitons
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["auth"])

