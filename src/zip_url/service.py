import base64
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.zip_url.repository import ZipURLRepository
from src.zip_url.models import ZippedURL
from src.user.schemas import UserRead
from src.zip_url.exceptions import TokenAlreadyExist
from src.core.config import config

class ZipURLService:
    def __init__(self, db: AsyncSession):
        self.zip_url_repository = ZipURLRepository(db)


    async def create_zip_url(self, original_url: str, user: UserRead, max_attempts=5) -> str:
        for _ in range(max_attempts):
            try:
                token = self._generate_token()
                zipped_url = ZippedURL(
                    original_url=original_url,
                    zip_token=token,
                    user_id=user.id,
                )
                zipped_url = await self.zip_url_repository.create_zip_url(zipped_url)
                return f"{config.get_base_url()}/{token}"
            except TokenAlreadyExist:
                pass
        raise RuntimeError("Could not generate a unique token")

    def _generate_token(self, length=16):
        return base64.urlsafe_b64encode(
            secrets.token_bytes(12)
        ).decode().rstrip("=")
    
    async def get_original_url_by_url_token(self, url_token) -> str | None:
        original_url = await self.zip_url_repository.get_zipped_url_by_url_token(url_token)
        return original_url.original_url