import pandas as pd
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Create processed directory if it doesn't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load datasets
movies = pd.read_csv(RAW_DIR / "movies.csv")
ratings = pd.read_csv(RAW_DIR / "ratings.csv")
tags = pd.read_csv(RAW_DIR / "tags.csv")
links = pd.read_csv(RAW_DIR / "links.csv")

# Basic inspection
print("Movies info:")
print(movies.info())

print("\nRatings info:")
print(ratings.info())

print("\nTags info:")
print(tags.info())

print("\nMissing values:")
print("Movies:\n", movies.isnull().sum())
print("Ratings:\n", ratings.isnull().sum())
print("Tags:\n", tags.isnull().sum())

# Remove duplicates
movies = movies.drop_duplicates()
ratings = ratings.drop_duplicates()
tags = tags.drop_duplicates()

# Select required columns
movies_clean = movies[["movieId", "title", "genres"]]
ratings_clean = ratings[["userId", "movieId", "rating"]]

# Clean tags text
tags["tag"] = tags["tag"].str.lower().str.strip()
tags_clean = tags[["userId", "movieId", "tag"]]

# Create edge list for graph-based algorithms
edges = ratings_clean[["userId", "movieId"]].drop_duplicates()

# Save processed files
movies_clean.to_csv(PROCESSED_DIR / "movies_clean.csv", index=False)
ratings_clean.to_csv(PROCESSED_DIR / "ratings_clean.csv", index=False)
tags_clean.to_csv(PROCESSED_DIR / "tags_clean.csv", index=False)
edges.to_csv(PROCESSED_DIR / "edges.csv", index=False)