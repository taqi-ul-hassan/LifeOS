from datetime import datetime, timezone


def authorization_url(provider, redirect_uri, state):
    return f"/{provider}/authorize?redirect_uri={redirect_uri}&state={state}"


def expired(expires_at: str | None):
    return bool(
        expires_at and datetime.fromisoformat(expires_at) <= datetime.now(timezone.utc)
    )
