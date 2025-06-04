import os
import logging

from fastapi import FastAPI
from dotenv import load_dotenv

from app.auth.handlers import router as auth_router
from app.user.handlers import router as user_router
from app.admin.handlers import router as admin_router
from app.asset.handlers import router as asset_router
from app.liability.handlers import router as liability_router
from app.portfolio.handlers import router as portfolio_router

from app.logger import setup_logger

# Setup logger
setup_logger()
logger = logging.getLogger(__name__)

# Run the App
app = FastAPI()

# App configuraitons
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(asset_router, prefix="/asset", tags=["asset"])
app.include_router(liability_router, prefix="/liability", tags=["liability"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])

logger.info("FastAPI application started successfully.")