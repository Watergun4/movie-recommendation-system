import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def add_new_rating(user_id, movie_id, rating):
    print("Adding/updating rating...")

    # Validate rating
    if rating < 0.5 or rating > 5.0:
        print("Error: Rating must be between 0.5 and 5.0")
        return

    ratings_path = PROCESSED_DIR / "ratings_clean.csv"
    ratings = pd.read_csv(ratings_path)

    # Check if user already rated this movie
    existing = (ratings['userId'] == user_id) & (ratings['movieId'] == movie_id)

    if existing.any():
        print("Existing rating found. Updating it...")
        ratings.loc[existing, 'rating'] = rating
    else:
        print("New rating. Adding it...")
        new_row = pd.DataFrame([{
            "userId": user_id,
            "movieId": movie_id,
            "rating": rating
        }])
        ratings = pd.concat([ratings, new_row], ignore_index=True)

    # Save updated ratings
    ratings.to_csv(ratings_path, index=False)
    print("Ratings updated successfully.")

    # Update edges
    update_edges(ratings)


def update_edges(ratings_df):
    print("Updating edges...")

    edges = ratings_df[['userId', 'movieId']]

    edges_path = PROCESSED_DIR / "edges.csv"
    edges.to_csv(edges_path, index=False)

    print("Edges updated successfully.")

if __name__ == "__main__":
    # Example usage:
    # add_new_rating(user_id=1, movie_id=1, rating=4.5)
    pass