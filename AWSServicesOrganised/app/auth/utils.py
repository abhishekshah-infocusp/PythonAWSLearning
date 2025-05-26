import base64
import hashlib
import hmac

from app.config import CLIENT_ID, CLIENT_SECRET

async def generate_secret_hash(username: str) -> str:

    message = username + CLIENT_ID
    digest = hmac.new(
        key=CLIENT_SECRET.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")
