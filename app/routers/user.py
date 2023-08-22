from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from ..database import get_db
from ..schemas import UserBase, UserShow, Token
from .. import models
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from ..auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "e007c5f110800d63681cd19e974af485c9193fd5d2016eccb4bd66a4bfbd734d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserShow)
def user_create(req: UserBase, db: Session = Depends(get_db)):
    payload = req.dict()
    payload["password"] = pwd_context.hash(req.password)
    user = db.query(models.User).filter(models.User.email == payload["email"]).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
            )
    user = models.User(**payload)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/update/{id}", status_code=status.HTTP_200_OK, response_model=UserShow)
def user_update(id: int, req: UserBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id)
    first_user = user.first()
    if not first_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id. {id} not found"
            )
    update_check = db.query(models.User).filter(models.User.email == req.email).first()
    if update_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
            )
    payload = req.dict()
    if req.password:
        payload["password"] = pwd_context.hash(req.password)
    user.update(payload, synchronize_session=False)
    db.commit()
    db.refresh(first_user)
    return first_user


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def user_delete(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id. {id} not found"
            )
    user.delete(synchronize_session=False)
    db.commit()
    return None


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
def login(payload: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect Credentials"
        )
    if not pwd_context.verify(payload.password, user.password):
        print(pwd_context.verify(payload.password, user.password))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect Credentials"
        )
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.email, "exp": expire}
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}
