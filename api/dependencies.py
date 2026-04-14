from fastapi import Header, HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()

API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "default_secret_token")

async def verify_api_token(x_api_token: str = Header(None)):
    if x_api_token != API_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Token",
        )
