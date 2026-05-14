from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models import User, EmailConfirmationToken, EmailStatus

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_confirmation_token(self, email_confirmation_token: EmailConfirmationToken) -> EmailConfirmationToken:
        self.db.add(email_confirmation_token)
        await self.db.commit()
        await self.db.refresh(email_confirmation_token)
        return email_confirmation_token
    
    async def activate_email_by_hashed_token(self, hashed_token: str) -> bool:
        stmt = select(EmailConfirmationToken).where(
            (EmailConfirmationToken.hashed_token==hashed_token) &
            (EmailConfirmationToken.used==False)
        )
        result = await self.db.execute(stmt)
        token_db = result.scalar_one_or_none()
        if not token_db: 
            return False
        
        stmt = select(User).where(User.id==token_db.user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False
        
        user.email_status = EmailStatus.ACTIVE
        token_db.used = True
        await self.db.commit()
        return True