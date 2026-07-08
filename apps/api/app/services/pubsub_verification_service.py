from typing import Any

from fastapi import HTTPException, status
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError, decode

from app.core.config import settings

GOOGLE_OIDC_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
VALID_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}


def verify_pubsub_oidc_token(authorization: str | None) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Pub/Sub bearer token")
    if not settings.pubsub_expected_audience or not settings.pubsub_service_account_email:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Pub/Sub auth is not configured")

    token = authorization.split(" ", 1)[1]
    try:
        jwks_client = PyJWKClient(GOOGLE_OIDC_CERTS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.pubsub_expected_audience,
            issuer=VALID_ISSUERS,
        )
    except (InvalidTokenError, PyJWKClientError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Pub/Sub bearer token") from exc

    if claims.get("email") != settings.pubsub_service_account_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unexpected Pub/Sub service account")
    return claims
