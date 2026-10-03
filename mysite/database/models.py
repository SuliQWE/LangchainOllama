from .database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SqlEnum
from typing import List
from datetime import datetime
import enum


class StatusChoices(str, enum.Enum):
    basic = 'basic'
    pro = 'pro'


class UserProfile(Base):
    __tablename__ = 'profile'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String)
    status: Mapped[StatusChoices] = mapped_column(SqlEnum(StatusChoices), default=StatusChoices.basic)
    registered_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_token: Mapped[List['RefreshToken']] = relationship(back_populates='token_user', cascade='all, delete-orphan')
    ai_usage: Mapped['ChatCount'] = relationship(back_populates='user', cascade='all, delete-orphan')
    user_files: Mapped[List['FileObject']] = relationship(back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'{self.username}'


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('profile.id'))
    token_user: Mapped['UserProfile'] = relationship('UserProfile', back_populates='user_token')
    token: Mapped[str] = mapped_column(String)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ChatCount(Base):
    __tablename__ = 'ai_chat_usage'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('profile.id'), unique=True)
    requests_count: Mapped[int] = mapped_column(Integer, default=0)
    last_request_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped['UserProfile'] = relationship(back_populates='ai_usage')

class FileObject(Base):
    __tablename__ = 'file_object'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_file: Mapped[str] = mapped_column(String)
    task_file: Mapped[str | None] = mapped_column(String, nullable=True)
    image_file: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('profile.id'))
    user: Mapped['UserProfile'] = relationship('UserProfile', back_populates='user_files')
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
