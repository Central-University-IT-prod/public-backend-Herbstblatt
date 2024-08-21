import os

from aiogram.utils.web_app import safe_parse_webapp_init_data, check_webapp_signature
from fastapi import APIRouter, HTTPException, Request
import pydantic

from ..utils.auth import gen_token


class SignInData(pydantic.BaseModel):
    login: str
    password: str


class TokenResponse(pydantic.BaseModel):
    token: str


BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

router = APIRouter()


@router.post("/auth/sign-in")
async def sign_in(request: Request) -> TokenResponse:
    data = (await request.body()).decode()

    try:
        result = safe_parse_webapp_init_data(BOT_TOKEN, data)
    except ValueError:
        raise HTTPException(status_code=401, detail="Credentials invalid")
    return TokenResponse(token=gen_token(result.user.id))
