from fastapi import FastAPI
from contextlib import asynccontextmanager
import aiosqlite
from endpoints import router
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aiosqlite.connect('database.db') as cursor:
        await cursor.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, total_screenshots INT, join_date TEXT)')
        await cursor.execute('CREATE TABLE IF NOT EXISTS screenshots(screenshot_name TEXT, screenshot_date TEXT, image_url TEXT, website_url TEXT, user_id INTEGER)')
        logging.info('Program start')
        yield
        logging.info('Program end')
app = FastAPI(lifespan=lifespan)

app.include_router(router)