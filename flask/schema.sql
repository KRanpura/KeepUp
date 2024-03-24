DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS interests;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    pass TEXT NOT NULL
);

CREATE TABLE interests (
    userid INTEGER,
    interest VARCHAR(30),
    PRIMARY KEY (userid, interest),
    FOREIGN KEY (userid) REFERENCES users(id)
);

-- CREATE TABLE posts (
--     id INTEGER PRIMARY KEY AUTOINCREMENT, 
--     content varchar(100)
-- )

-- CREATE TABLE posts (
--     id INTEGER PRIMARY KEY AUTOINCREMENT, 
--     userid INTEGER FOREIGN KEY REFERENCES users, 
--     content varchar(150)
-- )
-- finish later