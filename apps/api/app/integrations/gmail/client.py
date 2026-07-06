from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

GMAIL_API_BASE_URL = "https://gmail.googleapis.com/gmail/v1"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


async def refresh_gmail_access_token(refresh_token: str) -> tuple[str, datetime | None]:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth client credentials are not configured",
        )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach Google token endpoint from the API server",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token refresh failed")

    body = response.json()
    expires_in = body.get("expires_in")
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in) if expires_in else None
    return body["access_token"], expires_at


async def list_gmail_message_ids(
    access_token: str,
    label_ids: list[str],
    unread_only: bool,
    max_results: int = 20,
) -> list[str]:
    params: dict[str, Any] = {"maxResults": max_results}
    if label_ids:
        params["labelIds"] = label_ids
    if unread_only:
        params["q"] = "is:unread"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{GMAIL_API_BASE_URL}/users/me/messages",
                params=params,
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach Gmail messages endpoint from the API server",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gmail message list failed")

    return [message["id"] for message in response.json().get("messages", [])]


async def get_gmail_message(access_token: str, message_id: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{GMAIL_API_BASE_URL}/users/me/messages/{message_id}",
                params={"format": "full"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach Gmail message endpoint from the API server",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gmail message fetch failed")

    return response.json()

async def create_gmail_draft(access_token: str, raw_message: str, thread_id: str | None = None) -> dict[str, Any]:
    message: dict[str, Any] = {"raw": raw_message}
    if thread_id:
        message["threadId"] = thread_id

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{GMAIL_API_BASE_URL}/users/me/drafts",
                json={"message": message},
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach Gmail drafts endpoint from the API server",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gmail draft creation failed")

    return response.json()
