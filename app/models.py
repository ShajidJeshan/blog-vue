from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User") 

    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profile_pic = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'), nullable=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False, onupdate=text('now()'))
    Content = Column(String, nullable=False)

    user = relationship("User")

    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'), nullable=False)
