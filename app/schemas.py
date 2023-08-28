from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    password: str
    profile_pic: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserShow(BaseModel):
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
