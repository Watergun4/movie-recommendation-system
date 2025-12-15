from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .db import Base, engine, get_db, SessionLocal
from . import models, schemas, recommender
from .import_data import run_full_import

app = FastAPI(title="Movie Recommendation API")

# temporary homepage until frontend is finished
@app.get("/")
def read_root():
    return {"message": "Movie Recommendation API is running"}

# Create tables
Base.metadata.create_all(bind=engine)


def ensure_data_loaded():
    """
    Import CSV data into SQLite if the Movies table is empty.
    If anything goes wrong, print the error but don't stop the app.
    """
    db = SessionLocal()
    try:
        count = db.query(models.Movie).count()
        if count == 0:
            repo_root = Path(__file__).resolve().parents[2]
            data_dir = repo_root / "data" / "processed"
            print("Importing data from:", data_dir)
            if not data_dir.exists():
                print("WARNING: data directory not found:", data_dir)
                return
            run_full_import(db, data_dir)
            print("Data import finished.")
    except Exception as e:
        import traceback
        print("ERROR during ensure_data_loaded:", e)
        traceback.print_exc()
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # Don't let any error here crash the server
    ensure_data_loaded()


@app.on_event("startup")
def startup_event():
    # Don't let any error here crash the server
    ensure_data_loaded()


# ---------- USERS ----------

@app.post("/users", response_model=schemas.UserOut)
def create_or_get_user(payload: schemas.UserCreate,
                       db: Session = Depends(get_db)):
    """
    Creates the user if missing, otherwise returns existing.
    In our demo, user_id comes from MovieLens.
    """
    user = db.query(models.User).filter_by(user_id=payload.user_id).first()
    if not user:
        user = models.User(user_id=payload.user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ---------- MOVIES ----------

@app.get("/movies", response_model=List[schemas.MovieOut])
def search_movies(
    q: Optional[str] = Query(None, description="Title search keyword"),
    db: Session = Depends(get_db),
):
    """
    GET /movies?q=keyword
    Simple title search used by the Movie Search Page.
    """
    query = db.query(models.Movie)
    if q:
        # basic LIKE search
        query = query.filter(models.Movie.title.ilike(f"%{q}%"))
    return query.limit(50).all()


@app.get("/movies/{movie_id}", response_model=schemas.MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter_by(movie_id=movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


# ---------- WATCHED / INTERACTIONS ----------

@app.post("/users/{user_id}/watched")
def log_watched(
    user_id: int,
    payload: schemas.WatchedCreate,
    db: Session = Depends(get_db),
):
    """
    Stores that a user watched/rated a movie.
    Updates Ratings and Edges tables.
    """
    # ensure user exists
    user = db.query(models.User).filter_by(user_id=user_id).first()
    if not user:
        user = models.User(user_id=user_id)
        db.add(user)

    # ensure movie exists (in case of bad ID)
    movie = db.query(models.Movie).filter_by(movie_id=payload.movie_id).first()
    if not movie:
        raise HTTPException(status_code=400, detail="Movie does not exist")

    rating_value = payload.rating if payload.rating is not None else 4.0

    rating = models.Rating(
        user_id=user_id,
        movie_id=payload.movie_id,
        rating=rating_value,
    )
    edge = models.Edge(
        user_id=user_id,
        movie_id=payload.movie_id,
    )

    db.merge(rating)
    db.merge(edge)
    db.commit()
    return {"status": "ok"}


# ---------- RECOMMENDATIONS ----------

@app.get("/users/{user_id}/recommendations",
         response_model=List[schemas.RecommendationItem])
def get_recommendations(user_id: int,
                        db: Session = Depends(get_db)):
    """
    Returns top-N recommendations using graph-based CF.
    """
    recs = recommender.recommend_for_user(db, user_id=user_id, limit=10)
    return recs