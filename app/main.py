from fastapi import FastAPI
from .database import engine
from .routers import post, user, comment, follower
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(follower.router)
