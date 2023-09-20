from fastapi import APIRouter, status, Depends, HTTPException, Response
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import FollowerShow, FollowingShow
from .. import models
from ..auth import get_current_user


router = APIRouter(
    prefix="/follower",
    tags=["Follower"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FollowerShow)
def add_follower(user_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    follower_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
    follower_check = db.query(models.Follower).filter(and_(models.Follower.follower_id == follower_id, models.Follower.user_id == user_id))
    follower_check_first = follower_check.first()
    if follower_check_first:
        follower_check.delete(synchronize_session=False)
        db.commit()
        response = Response(content=None, status_code=204)
        return response
    follower = models.Follower(user_id=user_id, follower_id=follower_id)
    db.add(follower)
    db.commit()
    db.refresh(follower)
    return follower


@router.get("/all-followers/", status_code=status.HTTP_200_OK, response_model=List[FollowerShow])
def get_all_follower(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
    follower = db.query(models.Follower).filter(models.Follower.user_id == id).all()
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="follower doesn't exist"
            )
    return follower


@router.get("/all-following/", status_code=status.HTTP_200_OK, response_model=List[FollowingShow])
def get_all_following(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # user_id = db.query(models.User).filter(models.User.email == user["email"]).first().id
    following = db.query(models.Follower).filter(models.Follower.follower_id == id).all()
    if not following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following anyone"
            )
    return following
