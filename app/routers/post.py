from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PostBase, PostCreate, PostShow
from .. import models
from ..auth import get_current_user
import os
from PIL import Image

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostCreate)
def create_post(req: PostBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.email == user["email"]).first()
    new_post = models.Post(**req.model_dump(), user_id=user_query.id, user=user_query)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{user_id}/", status_code=status.HTTP_200_OK, response_model=List[PostShow])
def get_posts(user_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.user_id == user_id).all()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
            )
    return post


@router.get("/{id}/", status_code=status.HTTP_200_OK, response_model=PostCreate)
def get_specific_post(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id. {id} not found"
            )
    return post


@router.put("/update/{id}/", status_code=status.HTTP_200_OK, response_model=PostCreate)
def put_post(id: int, req: PostBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    first_post = post.first()
    user_id = db.query(models.User). filter(models.User.email == user["email"]).first().id
    if not first_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id. {id} not found"
            )
    if not user_id == first_post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
            )
    post.update(req.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(first_post)
    return first_post


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    user_id = db.query(models.User). filter(models.User.email == user["email"]).first().id
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id. {id} not found"
            )
    if not user_id == post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
            )
    post_query.delete(synchronize_session=False)
    db.commit()
    return None


IMAGEDIR = "images/posts/"


@router.patch("/post-media/", status_code=status.HTTP_201_CREATED)
async def post_media_upload(post_id: int, file: UploadFile, db: Session = Depends(get_db), user=Depends(get_current_user)):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    content_type = file.content_type

    if content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
    first_post = post_query.first()
    if not user_id == first_post.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
            )
    file.filename = f"{post_id}.webp"
    upload_dir = os.path.join(os.getcwd(), IMAGEDIR)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    dest = os.path.join(upload_dir, file.filename)
    image = Image.open(file.file)
    image.save(dest, format="webp")
    first_post.blog_media = dest
    db.commit()
    return {"filename": file.filename}
