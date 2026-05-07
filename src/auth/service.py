from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession


from src.user.schemas import UserCreate, UserLogin
from src.session.schemas import SessionRead
from src.user.service import UserService
from src.session.service import SessionService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_service = UserService(db)
        self.session_service = SessionService(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)


    async def register_user(self, user: UserCreate) -> SessionRead:
        created_user = await self.user_service.create_user(user)
        session = await self.session_service.create_session_by_user_id(created_user.id)
        return session
    
    async def login_user(self, user: UserLogin) -> SessionRead:     
        user_db = await self.user_service.check_password(user.email, user.password)
        session = await self.session_service.create_session_by_user_id(user_db.id)
        return session
    
    async def logout_user(self, session_token: str):
        success = await self.session_service.deactivate_session(session_token)
        return success




