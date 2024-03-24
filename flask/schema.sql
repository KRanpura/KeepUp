DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS articles;
DROP TABLE IF EXISTS saved;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    pass TEXT NOT NULL
);

CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(50),
    summary VARCHAR(500),
    link VARCHAR(255),
    img VARCHAR(15)
);

CREATE TABLE saved (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    postid INTEGER,
    userid INTEGER,
    link VARCHAR(255),
    FOREIGN KEY (postid) REFERENCES articles(id),
    FOREIGN KEY (userid) REFERENCES users(id)
    -- CONSTRAINT unique_saved_entry UNIQUE (postid, userid)
);
