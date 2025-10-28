from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from .config import settings
from .models_db import Base

# Асинхронный движок для SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Логирование SQL запросов (можно отключить в продакшене)
    future=True
)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Dependency для получения асинхронной сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def check_db_health() -> bool:
    """Проверка подключения к базе данных"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception:
        return False