from fastapi import APIRouter, HTTPException, status
from schemas import SNewScreenshot, SScreenshots, SScreenshots, SEditScreenshots
from functions import save_screenshot, CurrentUser
from database import Session
from models import User, Screenshot
from sqlalchemy import select, update, not_
from sqlalchemy.orm import selectinload

router = APIRouter(prefix='/screenshots')

@router.post('/new')#user: CurrentUser,
async def save_screenshot_endpoint(screenshot_info: SNewScreenshot, session: Session):
    user_id = 1 #user.id
    user_unfetched = await session.execute(select(User).where(User.id==user_id).options(selectinload(User.screenshots)))
    user = user_unfetched.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found!')
    image_url = await save_screenshot(user, screenshot_info)
    new_screenshot = Screenshot(name=screenshot_info.name, image_url=image_url, website_url=screenshot_info.url, user=user)
    screenshot_info.name = screenshot_info.name.replace(".", "")
    if not screenshot_info.name:
        screenshot_info.name = f'User_id={user_id}_{screenshot_info.url}'
    if not image_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='bad request!')
    user.screenshots.append(new_screenshot)
    await session.commit()
    return {'msg': 'success'}

@router.get('/')
async def get_user_screenshots(session: Session): #user: CurrentUser
    user_id = 1 #user.id
    user_unfetched = await session.execute(select(User).where(User.id==user_id).options(selectinload(User.screenshots)))
    user = user_unfetched.scalar_one_or_none()
    if not user:
        return {'msg': 'bad request'}
    screenshots = [i.to_dict() for i in user.screenshots if i.is_deleted==False]
    return {'screenshots': screenshots}

@router.get('/{screenshot_id}')
async def get_user_screenshot_by_id(screenshot_id: int, session: Session): #user: CurrentUser
    user_id = 1
    unfetched_screenshot = await session.execute(select(Screenshot).where(Screenshot.id == screenshot_id, Screenshot.user_id == user_id, not_(Screenshot.is_deleted))) #Screenshot.user_id == user.id
    screenshot = unfetched_screenshot.scalar_one_or_none()
    if not screenshot:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No screenshot with such id.')
    return {'msg': 'success', 'screenshot': screenshot}

@router.patch('/delete')
async def delete_screenshots(ids: SScreenshots, session: Session): #user: CurrentUser
    user_id = 1
    screenshots_to_delete_unfetched = await session.execute(select(Screenshot).where(Screenshot.id.in_(ids))) #позже сделать загрузку без атрибута is_deleted, user, user_id
    screenshots_to_delete = screenshots_to_delete_unfetched.scalars().all()
    if len(screenshots_to_delete) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No screenshots with such id(s) found!')
    screenshots = [str(screenshot) for screenshot in screenshots_to_delete]
    await session.execute(update(Screenshot).where(Screenshot.id.in_(ids.screenshot_ids), user_id == Screenshot.user_id).values(is_deleted=True)) #user.id
    await session.commit()
    return {'msg': 'success', 'screenshots deleted': screenshots}

@router.patch('/edit')
async def edit_screenshot(screenshots_info: SEditScreenshots, session: Session): #user: CurrentUser screenshots_info.to_change: dict[int, dict[str, str]]
    user_id = 1
    screenshots_unfetched = await session.execute(select(Screenshot).where(Screenshot.id.in_(list(screenshots_info.to_change.keys())), Screenshot.user_id == user_id, Screenshot.is_deleted == False))
    screenshots = screenshots_unfetched.scalars().all()
    return{'msg': f'Successfully changed screenshots with ids {list(screenshots_info.to_change.keys())}.', 'detail': screenshots_info.model_dump()}

@router.get('/test')
async def test(session: Session):
    result = []
    to_fetch = await session.execute(select(Screenshot))
    result.append(to_fetch.scalars().all())
    to_fetch = await session.execute(select(User))
    result.append(to_fetch.scalars().all())
    return result