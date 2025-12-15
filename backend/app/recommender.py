from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models

def recommend_for_user(db: Session, user_id: int, limit: int = 10, explain: bool = True):
    """
    Graph-based CF (overlap) using bipartite edges:
    1) Get movies watched by target user U
    2) Find other users who watched overlapping movies
    3) Aggregate candidate movies watched by those users
    4) Score by frequency
    5) Exclude already watched
    6) Return top-N
    """

    # Movies watched by target user
    watched_subq = (
        db.query(models.Edge.movie_id)
        .filter(models.Edge.user_id == user_id)
        .subquery()
    )

    # Similar users: users who watched any of U's movies
    similar_users_subq = (
        db.query(models.Edge.user_id)
        .filter(models.Edge.movie_id.in_(watched_subq))
        .filter(models.Edge.user_id != user_id)
        .distinct()
        .subquery()
    )

    # Candidate movies watched by similar users (excluding already watched)
    rows = (
        db.query(
            models.Movie.movie_id,
            models.Movie.title,
            func.count(models.Edge.user_id).label("score")
        )
        .join(models.Edge, models.Edge.movie_id == models.Movie.movie_id)
        .filter(models.Edge.user_id.in_(similar_users_subq))
        .filter(~models.Movie.movie_id.in_(watched_subq))
        .group_by(models.Movie.movie_id, models.Movie.title)
        .order_by(func.count(models.Edge.user_id).desc())
        .limit(limit)
        .all()
    )

    recs = []
    for movie_id, title, score in rows:
        item = {
            "movie_id": movie_id,
            "title": title,
            "score": int(score),
        }
        if explain:
            item["reasons"] = [f"Watched by {int(score)} similar users"]
        recs.append(item)

    return recs
