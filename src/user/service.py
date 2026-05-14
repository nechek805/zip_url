from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.schemas import UserCreate, UserRead
from src.user.repository import UserRepository
from src.user.exceptions import EmailAlreadyRegistered, EmailNotFound, PasswordNotValid
from src.user.models import User, EmailConfirmationToken
from src.core.config import config
from src.celery_app.celery_send_email import send_confirm_email



class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def _hash_token(sekf, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


    async def create_user(self, user: UserCreate):
        existing_user = await self.user_repository.get_user_by_email(user.email)

        if existing_user:
            raise EmailAlreadyRegistered()

        hashed_password = self._hash_password(user.password)

        user_model = User(
            email = user.email,
            hashed_password = hashed_password,
        )

        user_db = await self.user_repository.create_user(user_model)
        
        return UserRead.model_validate(user_db)
    

    async def check_password(self, email: str, password: str) -> User:
        user_db = await self.user_repository.get_user_by_email(email)
        if not user_db:
            raise EmailNotFound("Email not found")
        if not self.pwd_context.verify(password, user_db.hashed_password):
            raise PasswordNotValid("Password not valid")
        return user_db
    

    async def send_confirm_email(self, user: UserRead) -> bool:
        confirmation_token = secrets.token_urlsafe(32)
        message_subject = "Confirm your email"
        message_body = self._generate_confirm_email_text(confirmation_token)

        await self._create_email_confirmation_token(user.id, confirmation_token)

        send_confirm_email.delay(
            email=user.email,
            subject=message_subject,
            body=message_body
        )


    async def _create_email_confirmation_token(self, user_id: int, token: str) -> EmailConfirmationToken:
        hashed_token = self._hash_token(token)
        email_confirmation_token = EmailConfirmationToken(
            user_id=user_id,
            hashed_token=hashed_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        await self.user_repository.create_confirmation_token(email_confirmation_token)
        return email_confirmation_token


    def _generate_confirm_email_text(self, confirmation_token: str) -> str:
        confirmation_url = config.get_email_confirmation_url().format(token=confirmation_token)
        text = f"""
ZIP URL

Hello!

Please confirm your email by clicking this link:

{confirmation_url}

This link expires in 24 hours.
"""
        return text
    
    async def confirm_email(self, token: str) -> bool:
        hashed_token = self._hash_token(token)
        result = await self.user_repository.activate_email_by_hashed_token(hashed_token)
        return result

    