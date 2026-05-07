from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


from src.core.config import DATABASE_URL

class Base(DeclarativeBase):
    pass



engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
    )


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSession(engine) as session:
        try:
            yield session   
            await session.commit()
        except Exception:
            await session.rollback()
            raise