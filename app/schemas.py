from pydantic import BaseModel, EmailStr, HttpUrl  # Добавляем HttpUrl
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LinkBase(BaseModel):
    original_url: HttpUrl  # Изменяем тип на HttpUrl для валидации URL

class LinkCreate(LinkBase):
    expiry_date: Optional[datetime] = None

class Link(LinkBase):
    short_code: str
    expiry_date: Optional[datetime] = None
    user_id: int
    clicks: int = 0

    class Config:
        orm_mode = True

class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None  # Также обновляем для PUT-запроса
    expiry_date: Optional[datetime] = None

class LinkStats(BaseModel):
    original_url: str
    short_code: str
    clicks: int