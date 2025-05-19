CREATE DATABASE pn_database;
CREATE USER lucas WITH PASSWORD '1234';
ALTER DATABASE pn_database OWNER TO lucas;

\c pn_database
CREATE TABLE notes (
    tag NUMERIC(4) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    text TEXT NOT NULL
);
ALTER TABLE notes OWNER TO lucas;

