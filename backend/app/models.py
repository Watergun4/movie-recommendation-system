from sqlalchemy import Column, Integer, String, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, index=True)

class Movie(Base):
    __tablename__ = "Movies"
    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    genres = Column(String(255), nullable=True)

class Rating(Base):
    __tablename__ = "Ratings"
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("Movies.movie_id"), nullable=False)
    rating = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "movie_id"),
    )

class Tag(Base):
    __tablename__ = "Tags"
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("Movies.movie_id"), nullable=False)
    tag = Column(String(100), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "movie_id", "tag"),
    )

class Edge(Base):
    __tablename__ = "Edges"
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("Movies.movie_id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "movie_id"),
    )
