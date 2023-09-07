from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from sqlalchemy import desc
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import CommentData, CommentShow
from .. import models
from ..auth import get_current_user


router = APIRouter(
    prefix="/comment",
    tags=["Comment"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CommentShow)
def post_comment(req: CommentData, post_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    payload = req.model_dump()
    user_query = db.query(models.User).filter(models.User.email == user["email"]).first()
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post doesn't exist"
            )
    comment = models.Comment(**payload, post_id=post_id, user_id=user_query.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/{post_id}/", status_code= status.HTTP_200_OK, response_model=List[CommentShow])
def get_comment_by_id(post_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(desc(models.Comment.created_at)).all()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment doesn't exist"
            )
    return comment

  
@router.put("/update/", status_code=status.HTTP_200_OK, response_model=CommentShow)
def update_comment(req: CommentData, id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.id == id)
    user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
    comment = comment_query.first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment doesn't exist"
            )
    if not user_id == comment.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
            )
    comment_query.update(req.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
def comment_del(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == id)
    if not comment.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment doesn't exist"
            )
    comment.delete(synchronize_session=False)
    db.commit()
    return None
