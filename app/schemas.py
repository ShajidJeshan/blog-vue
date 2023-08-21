from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    body: str


class PostCreate(PostBase):
    
    class Config:
        orm_mode = True