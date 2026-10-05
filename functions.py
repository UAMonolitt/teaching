import jwt, httpx, bcrypt, asyncio, aiosqlite
from fastapi import HTTPException, status, Depends
from security import settings
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, UTC, timedelta
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from schemas import SScreenshot

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

OAuth2Bearer = Annotated[str, Depends(oauth2_scheme)]

options = Options()
options.add_argument('--headless=new')

driver = WebDriver(options=options)

async def check_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Signature expired!', headers={'WWW-Authenticate': 'Bearer'})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token!', headers={'WWW-Authenticate': 'Bearer'})
    return payload

async def get_user_info(token: OAuth2Bearer) -> dict:
    payload = await check_jwt(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong token', headers={'WWW-Authenticate': 'bearer'})
    async with aiosqlite.connect('database.db') as session:
        ids = await session.execute_fetchall('SELECT id FROM users')
        if not int(payload['sub']) in [int(*i) for i in ids]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong token1', headers={'WWW-Authenticate': 'bearer'})
    return payload

CurrentUser = Annotated[dict, Depends(get_user_info)]


async def get_jwt(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.EXPIRE_MINUTES)
    payload={
        'sub': str(user_id),
        'exp': expire
    }
    token = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def hash_pass(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password.encode('utf-8'), salt=salt).decode('utf-8')

async def add_image(user_id: int, screenshot_info: SScreenshot, screenshot_base64: str) -> dict:
    url = "https://api.imgbb.com/1/upload"

# Define your data payload here instead of the URL
    payload = {
    "key": settings.API_KEY,
    "image": screenshot_base64,
    "expiration": screenshot_info.delete_after
    }

    if screenshot_info.screenshot_name:
        payload['name'] = f'User_id: {user_id}. {screenshot_info.screenshot_name}'
    else:
        payload['name'] = f'User id: {user_id}. {url}'

    response = {}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
    return response.json()['data']

def _get_screenshot(url: str) -> str:
    try:
        driver.get(url)
        driver.fullscreen_window()
    except:
        try:
            driver.get(f'https://{url}')
            driver.fullscreen_window()
        except:
            return False
    return driver.get_screenshot_as_base64()

async def get_screenshot(url: str) -> str:
    if not (url.startswith('https://') or url.startswith('http://')):
        http_url = f'http://{url}'
        https_url = f'https://{url}'
        async with httpx.AsyncClient() as client:
            try:
                response_http = await client.head(http_url)
                if response_http.status_code == 200:
                    url = http_url
            except:
                try:
                    response_https = await client.head(https_url)
                    if response_https.status_code == 200:
                        url = https_url
                except: 
                    return False

    return await asyncio.to_thread(_get_screenshot, url=url)