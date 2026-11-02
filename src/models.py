from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import String, DateTime, func, ForeignKey, false, Boolean
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    screenshots: Mapped[list['Screenshot']] = relationship(back_populates='user')
    join_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default=false()) #new

    def to_dict(self) -> dict[str, any]:
        return {'id': self.id, 'username': self.username, 'screenshots': self.screenshots, 'join_date': self.join_date}
class Screenshot(Base):
    __tablename__ = 'screenshots'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    image_url: Mapped[str] = mapped_column(String(100), nullable=False)
    website_url: Mapped[str] = mapped_column(String(100), nullable=False, comment='URL of the website where screenshot was taken.')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='screenshots')
    public: Mapped[bool] = mapped_column(Boolean, server_default=false()) #added "Boolean"
    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default=false()) #added "Boolean"

    def to_dict(self) -> dict[str, any]:
        return {'screenshot_id': {self.id}, 'screenshot_name': {self.name}, 'screenshot_date': {self.date},
                'image_url': {self.image_url}, 'website_url': {self.website_url}}

class some_test_class(Base):
    __tablename__ = 'test_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))