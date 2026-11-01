from fastapi import FastAPI
from contextlib import asynccontextmanager
from screenshots_endpoints import router as screenshots_router
from user_endpoints import router as user_router
import logging
from database import engine
from models import Base

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    print('Program start')
    yield
    print('Program end')
        
app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(screenshots_router)