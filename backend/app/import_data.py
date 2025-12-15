import csv
from pathlib import Path
from typing import Optional  # <— for Optional[Path]

from sqlalchemy.orm import Session
from . import models


def _safe_int(x: str) -> int:
    return int(x.strip())


def _safe_float(x: str) -> float:
    return float(x.strip())


def import_movies(db: Session, path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie = models.Movie(
                movie_id=_safe_int(
                    row["movieId"] if "movieId" in row else row["movie_id"]
                ),
                title=row["title"],
                genres=row.get("genres", ""),
            )
            db.merge(movie)
    db.commit()


def import_users_from_ratings_edges(
    db: Session,
    ratings_path: Optional[Path],
    edges_path: Optional[Path],
) -> None:
    user_ids = set()

    if ratings_path and ratings_path.exists():
        with ratings_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_ids.add(
                    _safe_int(
                        row["userId"] if "userId" in row else row["user_id"]
                    )
                )

    if edges_path and edges_path.exists():
        with edges_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # edges.csv likely has columns: user_id,movie_id OR userId,movieId
            for row in reader:
                user_ids.add(
                    _safe_int(row.get("userId", row.get("user_id")))
                )

    for uid in user_ids:
        db.merge(models.User(user_id=uid))
    db.commit()


def import_ratings(db: Session, path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = _safe_int(row["userId"] if "userId" in row else row["user_id"])
            mid = _safe_int(row["movieId"] if "movieId" in row else row["movie_id"])
            rating_val = _safe_float(row["rating"])

            # ensure user exists
            db.merge(models.User(user_id=uid))
            rating = models.Rating(user_id=uid, movie_id=mid, rating=rating_val)
            db.merge(rating)
    db.commit()


def import_tags(db: Session, path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = _safe_int(row["userId"] if "userId" in row else row["user_id"])
            mid = _safe_int(row["movieId"] if "movieId" in row else row["movie_id"])
            tag = (row["tag"] or "").strip()

            if not tag:
                continue

            db.merge(models.User(user_id=uid))
            db.merge(models.Tag(user_id=uid, movie_id=mid, tag=tag))
    db.commit()


def import_edges(db: Session, path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = _safe_int(row.get("userId", row.get("user_id")))
            mid = _safe_int(row.get("movieId", row.get("movie_id")))

            db.merge(models.User(user_id=uid))
            db.merge(models.Edge(user_id=uid, movie_id=mid))
    db.commit()


def run_full_import(db: Session, data_dir: Path) -> None:
    movies_path = data_dir / "movies_clean.csv"
    ratings_path = data_dir / "ratings_clean.csv"
    tags_path = data_dir / "tags_clean.csv"
    edges_path = data_dir / "edges.csv"

    # 1) movies
    if movies_path.exists():
        import_movies(db, movies_path)

    # 2) users (inferred from ratings + edges)
    import_users_from_ratings_edges(
        db,
        ratings_path if ratings_path.exists() else None,
        edges_path if edges_path.exists() else None,
    )

    # 3) ratings
    if ratings_path.exists():
        import_ratings(db, ratings_path)

    # 4) tags
    if tags_path.exists():
        import_tags(db, tags_path)

    # 5) edges
    if edges_path.exists():
        import_edges(db, edges_path)
