from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from security import settings
from fastapi import Depends
from typing import Annotated

engine = create_async_engine(settings.DATABASE_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session

Session = Annotated[AsyncSession, Depends(get_session)]