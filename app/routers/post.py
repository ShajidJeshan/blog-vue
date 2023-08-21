from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PostBase, PostCreate
from .. import models

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostCreate)
def create_post(req: PostBase, db: Session = Depends(get_db)):
    new_post = models.Post(**req.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[PostCreate])
def get_posts(db: Session = Depends(get_db)):
    post = db.query(models.Post).all()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found")
    return post

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=PostCreate)
def get_specific_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id. {id} not found")
    return post


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=PostCreate)
def put_post(id: int, req: PostBase, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    first_post = post.first()
    if not first_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id. {id} not found")

    post.update(req.dict())
    db.commit()
    db.refresh(first_post)
    return first_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id. {id} not found")
    post.delete()
    db.commit()
    return None
