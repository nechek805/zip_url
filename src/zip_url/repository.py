from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.zip_url.models import ZippedURL
from src.zip_url.exceptions import TokenAlreadyExist

class ZipURLRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_zip_url(
            self,
            zipped_url: ZippedURL,
    ) -> ZippedURL:
        self.db.add(zipped_url)
        try:
            await self.db.commit()
            await self.db.refresh(zipped_url)
            return zipped_url
        except IntegrityError:
            raise TokenAlreadyExist("Token already exist")

    async def get_zipped_url_by_url_token(
            self,
            url_token: str,
    ) -> ZippedURL | None:
        stmt = select(ZippedURL).where(
            ZippedURL.zip_token==url_token
        )
        result = await self.db.execute(stmt)
        original_url = result.scalar_one_or_none()
        return original_url
    
    async def get_zip_urls_by_user_id(self, user_id: int) -> list[ZippedURL]:
        stmt = select(ZippedURL).where(
            ZippedURL.user_id==user_id
        )
        result = await self.db.execute(stmt)
        return result.scalars()