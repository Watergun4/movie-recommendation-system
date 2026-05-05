-- View sample data
SELECT * FROM Movies LIMIT 5;
SELECT * FROM Ratings LIMIT 5;
SELECT * FROM Tags LIMIT 5;
SELECT * FROM Edges LIMIT 5;

-- User watch history
SELECT m.title, r.rating
FROM Ratings r
JOIN Movies m ON r.movieId = m.movieId
WHERE r.userId = 1;

-- Top rated movies
SELECT m.title, AVG(r.rating) AS avg_rating
FROM Ratings r
JOIN Movies m ON r.movieId = m.movieId
GROUP BY m.movieId
ORDER BY avg_rating DESC
LIMIT 10;

-- Most popular movies
SELECT m.title, COUNT(*) AS num_ratings
FROM Ratings r
JOIN Movies m ON r.movieId = m.movieId
GROUP BY m.movieId
ORDER BY num_ratings DESC
LIMIT 10;

-- Tags for a movie
SELECT tag
FROM Tags
WHERE movieId = 60756;

-- Graph edges (for algorithm)
SELECT userId, movieId
FROM Edges
LIMIT 20;