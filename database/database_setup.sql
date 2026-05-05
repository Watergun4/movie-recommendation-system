CREATE TABLE "Movies" (
	"movieId"	INTEGER,
	"title"	TEXT,
	"genres"	TEXT,
	PRIMARY KEY("movieId")
)

CREATE TABLE "Ratings" (
	"userId"	INTEGER,
	"movieId"	INTEGER,
	"rating"	REAL,
	PRIMARY KEY("userId","movieId"),
	FOREIGN KEY("movieId") REFERENCES "Movies"("movieId")
)

CREATE TABLE "Edges" (
	"userId"	INTEGER,
	"movieId"	INTEGER,
	PRIMARY KEY("userId","movieId"),
	FOREIGN KEY("movieId") REFERENCES "Movies"("movieId")
)

CREATE TABLE "Tags" (
	"userId"	INTEGER,
	"movieId"	INTEGER,
	"tag"	TEXT,
	PRIMARY KEY("userId","movieId","tag"),
	FOREIGN KEY("movieId") REFERENCES "Movies"("movieId")
)