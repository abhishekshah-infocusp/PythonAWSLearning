import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Config for Cognito User Pool
CLIENT_ID = os.getenv("CLIENT_ID")
REGION = os.getenv("REGION")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERPOOL_ID = os.getenv("USERPOOL_ID")

# Config for AWS Users
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Config for S3 bucket
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION")
S3_BASE_URL = os.getenv("S3_BASE_URL")
S3_PROFILE_PIC_FOLDER = os.getenv("S3_PROFILE_PIC_FOLDER")
