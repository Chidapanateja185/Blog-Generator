from typing import List
from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import JWTError

from src.core.database import get_db
from src.models.users import Users
from src.core.security import decode_token

from src.utlis.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
)


class TokenBearer(HTTPBearer):

    async def __call__(self, request: Request) -> dict:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)

        if not creds:
            raise InvalidToken()

        token = creds.credentials

        try:
            payload = decode_token(token)
        except JWTError:
            raise InvalidToken()

        payload["raw"] = token

        self.verify_token_data(payload)

        return payload

    def verify_token_data(self, payload: dict):
        raise NotImplementedError()


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict):
        if payload.get("type") != "access":
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict):
        if payload.get("type") != "refresh":
            raise RefreshTokenRequired()


async def get_current_user(token: dict = Depends(AccessTokenBearer()), db=Depends(get_db)) -> Users:

    user = db.query(Users).filter(Users.email == token.get("email")).first()

    if not user:
        raise InvalidToken()

    return user


class RoleChecker:
    def __init__(self, roles: List[str]):
        self.roles = roles

    def __call__(self, user: Users = Depends(get_current_user)):

        if user.role.value not in self.roles:
            raise InsufficientPermission()

        return user