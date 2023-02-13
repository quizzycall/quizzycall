from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from security.config import Config as cfg
engine = create_async_engine(cfg.PSQL_URL, pool_pre_ping=True, echo=True, future=True)
async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
metadata = SQLModel.metadata


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
