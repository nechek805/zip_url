
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.session.models import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, session: Session) -> Session:
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def get_session_by_hashed_session_token(hashed_session_token: str) -> Session:
        session = await select(Session).where(Session.hashed_session_token==hashed_session_token)
        return session
    
    async def deactivate_session(self, session: Session) -> Session:
        session.is_active = False
        await self.db.commit()
        await self.db.refresh(session)
        return session


    