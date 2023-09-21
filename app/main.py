from fastapi import FastAPI
from .database import engine
from .routers import post, user, comment, follower
from . import models
import uvicorn
from fastapi_pagination import add_pagination

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
add_pagination(app)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(follower.router)


if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)
