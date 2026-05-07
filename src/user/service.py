from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.schemas import UserCreate, UserRead
from src.user.repository import UserRepository
from src.user.exceptions import EmailAlreadyRegistered, EmailNotFound, PasswordNotValid
from src.user.models import User
from src.logger import logger

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository = UserRepository(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)


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
        hashed_password = self._hash_password(password)
        logger.info(f"{hashed_password=}, {user_db.hashed_password=}")
        if not self.pwd_context.verify(password, user_db.hashed_password):
            raise PasswordNotValid("Password not valid")
        return user_db
    

    