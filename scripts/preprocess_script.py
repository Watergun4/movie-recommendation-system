import pandas as pd
from pathlib import Path

# -------------------------
# PATH SETUP
# -------------------------

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Create processed folder if it doesn't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Loading datasets...")

movies = pd.read_csv(RAW_DATA_DIR / "movies.csv")
ratings = pd.read_csv(RAW_DATA_DIR / "ratings.csv")
tags = pd.read_csv(RAW_DATA_DIR / "tags.csv")
links = pd.read_csv(RAW_DATA_DIR / "links.csv")

print("Datasets loaded successfully.\n")

# -------------------------
# VALIDATION
# -------------------------

print("Running validation checks...\n")

# Missing values
print("Missing values:")
print("Movies:\n", movies.isnull().sum())
print("Ratings:\n", ratings.isnull().sum())
print("Tags:\n", tags.isnull().sum())
print()

# Duplicate check
print("Duplicate rows:")
print("Movies:", movies.duplicated().sum())
print("Ratings:", ratings.duplicated().sum())
print("Tags:", tags.duplicated().sum())
print()

# Rating range check
invalid_ratings = ratings[(ratings['rating'] < 0.5) | (ratings['rating'] > 5.0)]
print("Invalid ratings count:", len(invalid_ratings))
print()

# -------------------------
# CLEANING
# -------------------------

movies = movies.drop_duplicates()
ratings = ratings.drop_duplicates()
tags = tags.drop_duplicates()

# Select relevant columns
movies_clean = movies[['movieId', 'title', 'genres']]
ratings_clean = ratings[['userId', 'movieId', 'rating']]

# Clean tags
tags['tag'] = tags['tag'].str.lower().str.strip()
tags_clean = tags[['userId', 'movieId', 'tag']]

# Create edge list
edges = ratings_clean[['userId', 'movieId']]

# Remove empty rows
edges = edges.dropna()

# -------------------------
# SAVE FILES
# -------------------------

print("Saving processed files...")

movies_clean.to_csv(PROCESSED_DIR / "movies_clean.csv", index=False)
ratings_clean.to_csv(PROCESSED_DIR / "ratings_clean.csv", index=False)
tags_clean.to_csv(PROCESSED_DIR / "tags_clean.csv", index=False)
edges.to_csv(PROCESSED_DIR / "edges.csv", index=False)

print("Files saved successfully.\n")

# -------------------------
# FINAL SUMMARY
# -------------------------

print("Final dataset summary:")
print(f"Movies: {len(movies_clean)}")
print(f"Ratings: {len(ratings_clean)}")
print(f"Tags: {len(tags_clean)}")
print(f"Edges: {len(edges)}")

print("\nPreprocessing completed successfully.")