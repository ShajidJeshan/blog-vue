from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, text, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blog_media = Column(String, nullable=True, server_default=None)
    like_count = Column(Integer, nullable=True, default=0)
    comment_count = Column(Integer, nullable=True, default=0)

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
    follower_count = Column(Integer, nullable=True, default=0)

    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'), nullable=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    like_count = Column(Integer, nullable=True, default=0)

    user = relationship("User")

    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text('now()'), onupdate=text('now()'), nullable=False)


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)


class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    comment_id = Column(Integer, ForeignKey('comments.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)


class Follower(Base):
    __tablename__ = "followers"

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, primary_key=True)
    follower_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'), nullable=False)

    user = relationship('User', foreign_keys=[user_id])
    follower = relationship('User', foreign_keys=[follower_id])

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'follower_id'),
    )