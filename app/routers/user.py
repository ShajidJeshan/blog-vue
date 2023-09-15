from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserBase, UserShow, Token
from .. import models
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from ..auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
import os
import shutil


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Command for generating secret key "openssl rand -hex 32"
SECRET_KEY = "e007c5f110800d63681cd19e974af485c9193fd5d2016eccb4bd66a4bfbd734d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserShow)
def user_create(req: UserBase, db: Session = Depends(get_db)):
    payload = req.model_dump()
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


@router.put("/update/{id}/", status_code=status.HTTP_200_OK, response_model=UserShow)
def user_update(id: int, req: UserBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    first_user = user_query.first()
    update_check = db.query(models.User).filter(models.User.email == req.email).first()
    if not first_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id. {id} not found"
            )
    if update_check and first_user.email == user["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
            )
    if not first_user.email == user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
            )
    payload = req.model_dump()
    if req.password:
        payload["password"] = pwd_context.hash(req.password)
    user_query.update(payload, synchronize_session=False)
    db.commit()
    db.refresh(first_user)
    return first_user


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def user_delete(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    first_user = user_query.first()
    if not first_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User of id. {id} not found"
            )
    if not first_user.email == user["email"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
            )
    user_query.delete(synchronize_session=False)
    db.commit()
    return None


@router.post("/login", status_code=status.HTTP_201_CREATED, response_model=Token)
def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    print(to_encode)
    return {"access_token": access_token, "token_type": "bearer"}


IMAGEDIR = "images/users/"


@router.post("/profile-pic/", status_code=status.HTTP_201_CREATED)
async def user_profile_pic(file: UploadFile, db: Session = Depends(get_db), user=Depends(get_current_user)):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    if file_size > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    content_type = file.content_type

    if content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    user_query = db.query(models.User).filter(models.User.email == user["email"])
    first_user = user_query.first()
    user_id = first_user.id
    suffix = file.filename.split(".")[-1]
    file.filename = f"{user_id}.{suffix}"
    upload_dir = os.path.join(os.getcwd(), IMAGEDIR)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    dest = os.path.join(upload_dir, file.filename)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    first_user.profile_pic = dest
    db.commit()
    return {"filename": file.filename}
