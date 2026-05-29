import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"

# Create docs folder if it doesn't exist
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Load data
ratings = pd.read_csv(PROCESSED_DIR / "ratings_clean.csv")
movies = pd.read_csv(PROCESSED_DIR / "movies_clean.csv")

print("Datasets loaded successfully.")


# 1. Ratings distribution
plt.figure(figsize=(8, 5))

ratings['rating'].hist(bins=10)

plt.title("Ratings Distribution")
plt.xlabel("Rating")
plt.ylabel("Frequency")

plt.savefig(DOCS_DIR / "ratings_distribution.png")

plt.close()

print("Saved ratings_distribution.png")


# 2. Ratings per user
ratings_per_user = ratings.groupby('userId').size()

plt.figure(figsize=(8, 5))

ratings_per_user.hist(bins=30)

plt.title("Ratings Per User")
plt.xlabel("Number of Ratings")
plt.ylabel("Number of Users")

plt.savefig(DOCS_DIR / "ratings_per_user.png")

plt.close()

print("Saved ratings_per_user.png")


# 3. Genre frequency
genres = movies['genres'].str.split('|').explode()

genre_counts = genres.value_counts().head(10)

plt.figure(figsize=(10, 6))

genre_counts.plot(kind='bar')

plt.title("Top 10 Movie Genres")
plt.xlabel("Genre")
plt.ylabel("Count")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(DOCS_DIR / "genre_frequency.png")

plt.close()

print("Saved genre_frequency.png")

# Finished
print("\nAll visualizations generated successfully.")