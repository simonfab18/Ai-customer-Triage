from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError, decode
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


class AuthenticatedUser(BaseModel):
    id: str
    email: str | None = None


def decode_unverified_local_token(token: str) -> dict:
    if settings.app_env != "local" or not settings.auth_allow_unverified_jwt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return decode(
        token,
        options={
            "verify_signature": False,
            "verify_aud": False,
            "verify_exp": False,
        },
    )


def decode_supabase_token(token: str) -> dict:
    try:
        if settings.supabase_jwks_url:
            jwks_client = PyJWKClient(settings.supabase_jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            return decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                options={"verify_aud": False},
            )

        if settings.supabase_jwt_secret:
            return decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
    except (InvalidTokenError, PyJWKClientError):
        return decode_unverified_local_token(token)

    if settings.auth_allow_unverified_jwt:
        return decode_unverified_local_token(token)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth is not configured")


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> AuthenticatedUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    claims = decode_supabase_token(token)

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")

    return AuthenticatedUser(id=user_id, email=claims.get("email"))


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
