from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship, selectinload
from sqlalchemy import ForeignKey, select, update, delete, insert
import asyncio

DATABASE_URL = 'postgresql+asyncpg://postgres:UssRRu1991@localhost:5432/screenshoter_db'

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    orders: Mapped[list['Order']] = relationship(back_populates='user')

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='orders')

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        new_user = User(username='UAMonolit3', password='My_pass')
        new_user.orders.append(Order(name='Keyboard'))
        new_user.orders.append(Order(name='Mouse'))
        session.add(new_user)
        await session.commit()

    async with async_session() as session:
        query = select(User).where(User.username=='UAMonolit3').options(selectinload(User.orders))
        result = await session.execute(query)
        user = result.scalars().first()
        print(user.id, user.username, user.password, user.orders)
        for i in user.orders:
            print(i.id, i.name, i.user_id, i.user)

        query = select(Order)
        result = await session.execute(query)
        orders = result.scalars().all()
        for i in orders:
            print(i.id, i.name, i.user_id, i.user)
if __name__ == '__main__':
    asyncio.run(main())