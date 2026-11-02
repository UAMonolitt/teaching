import pytest, asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from src.models import Base
from src.main import app
from src.database import get_session
from httpx import AsyncClient, ASGITransport

DATABASE_URL = 'sqlite+aiosqlite:///:memory:'
engine = create_async_engine(DATABASE_URL, poolclass=StaticPool, connect_args={'check_same_thread': False})
async_session = async_sessionmaker(engine, expire_on_commit=False)

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session', autouse=True)
async def config_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def get_test_session():
    connection = await engine.connect()
    transaction = await connection.begin()
    session = async_session(bind=connection)
    yield session
    await session.close()
    await transaction.commit()
    await connection.close()

@pytest.fixture(autouse=True)
async def override_db_dependency(get_test_session):
    async def override_session():
        yield get_test_session

    app.dependency_overrides[get_session] = override_session
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope='session')
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as test_client:
        yield test_client