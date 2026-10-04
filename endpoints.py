from fastapi import APIRouter, HTTPException, status
from schemas import SRegisterLogin
from datetime import datetime, UTC
import aiosqlite, bcrypt
from functions import add_image, get_jwt, CurrentUser, hash_pass, get_screenshot

router = APIRouter()

@router.get('/save_screenshot')
async def save_screenshot_endpoint(url: str, screenshot_name: str | None = None):
    user_id = 1 #make id system later
    result = await get_screenshot(url)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No website with such URL.')
    async with aiosqlite.connect('database.db') as cursor:
        json_result = await add_image(screenshot_name)
        await cursor.execute('INSERT INTO screenshots VALUES (?, ?, ?, ?, ?)', (screenshot_name, datetime.now(UTC), json_result['url'], url, user_id))
        await cursor.commit()
    return json_result

@router.post('/register')
async def register(register_schema: SRegisterLogin):
    async with aiosqlite.connect('database.db') as cursor:
        check_user = await cursor.execute_fetchall('SELECT * FROM users WHERE name=?', (register_schema.username,))
        if check_user and len(check_user) >= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You are already registered.')
        hashed_pass = hash_pass(register_schema.password)
        hashed_pass = hashed_pass.decode('utf-8')
        new_user_id = await cursor.execute_insert('INSERT INTO users(name, password, total_screenshots, join_date) VALUES (?, ?, ?, ?)', (register_schema.username, hashed_pass, 0, datetime.now(UTC)))
        await cursor.commit()
        new_user = await cursor.execute_fetchall('SELECT * FROM users WHERE id=?', new_user_id)
        return new_user

@router.post('/login')
async def login(login_schema: SRegisterLogin):
    async with aiosqlite.connect('database.db') as cursor:
        to_fetch = await cursor.execute('SELECT id, password FROM users WHERE name=?', (login_schema.username,))
        user = await to_fetch.fetchone()
        if not user or len(user) < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong username or password.')
        if bcrypt.checkpw(password=login_schema.password.encode('utf-8'), hashed_password=user[1].encode('utf-8')):
            token = await get_jwt(user[0])
            return {'msg': 'success', 'token': token}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong username or password.')
# i stoppped here
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