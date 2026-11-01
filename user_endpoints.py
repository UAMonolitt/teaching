from fastapi import APIRouter, HTTPException, status
from security import settings
from functions import Session, CurrentUser, get_jwt, hash_pass
from sqlalchemy import select, not_
from sqlalchemy.orm import selectinload
from models import User, Screenshot
from schemas import SRegister, SLogin, SNewPassword, SAccountSettings, SDeleteAccount
import bcrypt

router = APIRouter()

@router.post('/test_token')
async def test_token(user_info: CurrentUser):
    print(user_info)
    return user_info

@router.post('/register')
async def register(register_schema: SRegister, session: Session):
    user_unfetched = await session.execute(select(User).where(User.username==register_schema.username))
    user = user_unfetched.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You are already registered.')
    hashed_pass = hash_pass(register_schema.password)
    new_user = User(username=register_schema.username, password=hashed_pass)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.post('/login')
async def login(login_schema: SLogin, session: Session):
    user_unfetched = await session.execute(select(User).where(User.username==login_schema.username))
    user = user_unfetched.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong username or password.')
    if bcrypt.checkpw(password=login_schema.password.encode('utf-8'), hashed_password=user.password.encode('utf-8')):
        token = await get_jwt(user.id)
        return {'msg': 'success', 'token': token}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong username or password.')

@router.get('/account')
async def get_account(session: Session): #user: CurrentUser
    user_id = 1
    user_unfetched = await session.execute(select(User).where(User.id == user_id, not_(User.is_deleted)).options(selectinload(User.screenshots)))
    user = user_unfetched.scalars().first()
    return {'user': user.to_dict()}

@router.patch('/account/settings')
async def account_settings(account_settings: SAccountSettings, session: Session): #user: CurrentUser
    user_id = 1
    user_unfetched = await session.execute(select(User).where(User.id==user_id))
    user = user_unfetched.scalars().first()
    if not bcrypt.checkpw(account_settings.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong password!')
    if account_settings.new_username:
        user.username = account_settings.new_username
    await session.commit()


@router.patch('/account/delete')
async def delete_account(password_schema: SDeleteAccount, session: Session): #user: CurrentUser
    user_id = 1
    user_unfetched = await session.execute(select(User).where(User.id==user_id))
    user = user_unfetched.scalars().first()
    if bcrypt.checkpw(password_schema.password.encode('utf-8'), user.password.encode('utf-8')):
        user.is_deleted = True
    await session.commit()
    return {'msg': f'Successfully deleted account with user id {user.id}'}

@router.patch('/account/change-password')
async def change_account_password(password_schema: SNewPassword, session: Session): #user: CurrentUser
    user_id = 1
    user_unfetched = await session.execute(select(User).where(User.id==user_id))
    user = user_unfetched.scalars().first()
    if bcrypt.checkpw(password_schema.old_password.encode('utf-8'), user.password.encode('utf-8')) and password_schema.new_password == password_schema.confirm_new_password:
        user.password = password_schema.new_password
    await session.commit()