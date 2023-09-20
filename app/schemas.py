from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    password: str
    profile_pic: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserShow(BaseModel):
    id: int
    email: EmailStr
    username: str
    profile_pic: str

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    body: str


class PostCreate(BaseModel):
    title: str
    body: str
    blog_media: str | None
    user: UserShow

    class Config:
        from_attributes = True


class PostShow(BaseModel):
    title: str
    body: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    email: EmailStr


class CommentData(BaseModel):
    content: str


class CommentShow(CommentData):
    id: int
    user: UserShow
    created_at: datetime

    class cofig:
        form_attribute = True


class FollowerShow(BaseModel):
    user_id: int
    follower_id: int
    follower: UserShow
    created_at: datetime

    class config:
        form_attribute = True


class FollowingShow(BaseModel):
    user_id: int
    follower_id: int
    user: UserShow
    created_at: datetime

    class config:
        form_attribute = True
