import jwt, httpx, bcrypt, asyncio
from fastapi import HTTPException, status, Depends
from security import settings
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, UTC, timedelta
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from schemas import SNewScreenshot
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import Session
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

OAuth2Bearer = Annotated[str, Depends(oauth2_scheme)]

options = Options()
options.add_argument('--headless=new')

driver = WebDriver(options=options)

driver.close()

async def check_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Signature expired!', headers={'WWW-Authenticate': 'Bearer'})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token!', headers={'WWW-Authenticate': 'Bearer'})
    return payload

async def get_user(token: OAuth2Bearer, session: Session) -> dict:
    payload = await check_jwt(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong token', headers={'WWW-Authenticate': 'bearer'})
    user_unfetched = await session.execute(select(User).where(User.id==int(payload['sub'])).options(selectinload(User.screenshots)))
    user = user_unfetched.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong token!', headers={'WWW-Authenticate': 'bearer'})
    return payload

CurrentUser = Annotated[dict, Depends(get_user)]


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

def _save_screenshot(user: User, screenshot_info: SNewScreenshot) -> bool | None:
    screenshot_url = f'pictures/user_id_{user.id}-{screenshot_info.screenshot_name}-#{len(user.screenshots)}.png'
    try:
        print(1)
        driver.get(screenshot_info.url)
        driver.fullscreen_window()
    except:
        try:
            print(2)
            driver.get(f'https://{screenshot_info.url}')
            driver.fullscreen_window()
        except:
            return False
    driver.save_screenshot(screenshot_url)
    return screenshot_url

async def save_screenshot(user: User, screenshot_info: SNewScreenshot) -> bool | None:
    if not (screenshot_info.url.startswith('https://') or screenshot_info.url.startswith('http://')):
        http_url = f'http://{screenshot_info.url}'
        https_url = f'https://{screenshot_info.url}'
        async with httpx.AsyncClient() as client:
            try:
                response_http = await client.head(http_url)
                if response_http.status_code == 200:
                    screenshot_info.url = http_url
            except:
                try:
                    response_https = await client.head(https_url)
                    if response_https.status_code == 200:
                        screenshot_info.url = https_url
                except: 
                    print(3)
                    return False
    return await asyncio.to_thread(_save_screenshot, user, screenshot_info)