from fastapi import APIRouter, status, Depends, HTTPException, Response
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import FollowerShow
from .. import models
from ..auth import get_current_user


router = APIRouter(
    prefix="/follower",
    tags=["Follower"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FollowerShow)
def add_follower(user_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    follower_query = db.query(models.User).filter(models.User.email == user["email"]).first()
    follower_check = db.query(models.Follower).filter(and_(models.Follower.follower_id == follower_query.id, models.Follower.user_id == user_id))
    follower_check_first = follower_check.first()
    if follower_check_first:
        follower_check.delete(synchronize_session=False)
        db.commit()
        response = Response(content={"details": "User unfollowed"}, status_code=204)
        return response
    follower = models.Follower(user_id=user_id, follower_id=follower_query.id)
    db.add(follower)
    db.commit()
    db.refresh(follower)
    return follower


@router.get("/all-followers/", status_code=status.HTTP_200_OK, response_model=List[FollowerShow])
def get_all_follower(db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
    follower = db.query(models.Follower).filter(models.Follower.user_id == user_id).all()
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="follower doesn't exist"
            )
    return follower

  
# @router.put("/update/", status_code=status.HTTP_200_OK, response_model=CommentShow)
# def update_comment(req: CommentData, id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     comment_query = db.query(models.Comment).filter(models.Comment.id == id)
#     user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
#     comment = comment_query.first()
#     if not comment:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Comment doesn't exist"
#             )
#     if not user_id == comment.user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Unauthorized"
#             )
#     comment_query.update(req.model_dump(), synchronize_session=False)
#     db.commit()
#     db.refresh(comment)
#     return comment


# @router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
# def comment_del(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     comment_query = db.query(models.Comment).filter(models.Comment.id == id)
#     comment = comment_query.first()
#     user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
#     post_user_id = db.query(models.Post).filter(models.Post.id == comment.post_id).first().user_id
#     if not comment:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Comment doesn't exist"
#             )
#     if not (user_id == post_user_id or user_id == comment.user_id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Unauthorized"
#             )
#     comment_query.delete(synchronize_session=False)
#     db.commit()
#     return None
