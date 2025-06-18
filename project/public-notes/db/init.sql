CREATE DATABASE pn_database;
CREATE USER lucas WITH PASSWORD '1234';
ALTER DATABASE pn_database OWNER TO lucas;

\c pn_database
CREATE TABLE notes (
    tag NUMERIC(4) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    text TEXT NOT NULL
);
ALTER TABLE notes OWNER TO lucas;

INSERT INTO notes (tag, title, name, email, text) VALUES ('0','exemplo de título', 'lucas', 'lucas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('1','Meeting Notes', 'Maria', 'maria@company.com', 'Discussed project timeline');
INSERT INTO notes (tag, title, name, email, text) VALUES ('2','Shopping List', 'João', 'joao@gmail.com', 'Milk, eggs, bread');
INSERT INTO notes (tag, title, name, email, text) VALUES ('3','Ideas Blog', 'Ana', 'ana@blog.org', 'Content ideas for next month');
INSERT INTO notes (tag, title, name, email, text) VALUES ('4','Work Tasks', 'Carlos', 'carlos@work.net', 'Finish report by Friday');
INSERT INTO notes (tag, title, name, email, text) VALUES ('5','Travel Plans', 'Julia', 'julia@travel.com', 'Book flight to Paris');
INSERT INTO notes (tag, title, name, email, text) VALUES ('6','Study Notes', 'Pedro', 'pedro@university.edu', 'Math formulas to remember');
INSERT INTO notes (tag, title, name, email, text) VALUES ('7','Recipe', 'Fernanda', 'fernanda@food.net', 'Grandms cake recipe');
INSERT INTO notes (tag, title, name, email, text) VALUES ('8','Book Recommendations', 'Ricardo', 'ricardo@books.com', 'New sci-fi releases');
INSERT INTO notes (tag, title, name, email, text) VALUES ('9','Project Ideas', 'Camila', 'camila@dev.io', 'Mobile app for task management');

