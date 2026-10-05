from fastapi import APIRouter, HTTPException, status
from schemas import SRegister, SLogin, SScreenshot
from datetime import datetime, UTC
import aiosqlite, bcrypt
from functions import add_image, get_jwt, CurrentUser, hash_pass, get_screenshot

router = APIRouter()

@router.post('/save_screenshot')
async def save_screenshot_endpoint(user_info: CurrentUser, screenshot_info: SScreenshot):
    user_id = int(user_info['sub'])
    screenshot_base64 = await get_screenshot(screenshot_info.url)
    if not screenshot_base64:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No website with such URL.')
    async with aiosqlite.connect('database.db') as session:
        json_result = await add_image(user_id, screenshot_info, screenshot_base64)
        await session.execute('INSERT INTO screenshots VALUES (?, ?, ?, ?, ?, ?)', (screenshot_info.screenshot_name, datetime.now(UTC), json_result['url'], screenshot_info.url, user_id, screenshot_info.delete_after))
        await session.commit()
    return json_result

@router.post('/register')
async def register(register_schema: SRegister):
    async with aiosqlite.connect('database.db') as cursor:
        check_user = await cursor.execute_fetchall('SELECT * FROM users WHERE name=?', (register_schema.username,))
        if check_user and len(check_user) >= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You are already registered.')
        hashed_pass = hash_pass(register_schema.password)
        new_user_id = await cursor.execute_insert('INSERT INTO users(name, password, total_screenshots, join_date) VALUES (?, ?, ?, ?)', (register_schema.username, hashed_pass, 0, datetime.now(UTC)))
        await cursor.commit()
        new_user = await cursor.execute_fetchall('SELECT * FROM users WHERE id=?', new_user_id)
        return new_user

@router.post('/login')
async def login(login_schema: SLogin):
    async with aiosqlite.connect('database.db') as cursor:
        to_fetch = await cursor.execute('SELECT id, password FROM users WHERE name=?', (login_schema.username,))
        user = await to_fetch.fetchone()
        if not user or len(user) < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong username or password.')
        if bcrypt.checkpw(password=login_schema.password.encode('utf-8'), hashed_password=user[1].encode('utf-8')):
            token = await get_jwt(user[0])
            return {'msg': 'success', 'token': token}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong username or password.')

@router.get('/test')
async def test():
    async with aiosqlite.connect('database.db') as cursor:
        result = []
        to_fetch = await cursor.execute('SELECT * FROM screenshots')
        result.append(await to_fetch.fetchall())
        to_fetch = await cursor.execute('SELECT * FROM users')
        result.append(await to_fetch.fetchall())
    return result

@router.post('/del_all')
async def drop_all():
    async with aiosqlite.connect('database.db') as cursor:
        await cursor.execute('DROP TABLE IF EXISTS users')
        await cursor.execute('DROP TABLE IF EXISTS screenshots')
    return {'msg': 'success'}

@router.post('/test_token')
async def test_token(user_info: CurrentUser):
    print(user_info)
    return user_info