from datetime import datetime

from pydantic import BaseModel

class ZipURLFullInfo(BaseModel):
    id: int
    original_url: str
    zipped_url: str
    created_at: datetime