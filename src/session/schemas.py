from datetime import datetime

from pydantic import BaseModel


class SessionRead(BaseModel):
    session_token: str
    created_at: datetime
    expires_at: datetime