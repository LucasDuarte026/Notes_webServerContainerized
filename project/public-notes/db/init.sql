CREATE DATABASE pn_database;
CREATE USER lucas WITH PASSWORD '1234';
ALTER DATABASE pn_database OWNER TO lucas;

\c pn_database
CREATE TABLE notes (
    tag NUMERIC(4) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    text TEXT NOT NULL
);
ALTER TABLE notes OWNER TO lucas;

INSERT INTO notes (tag, title, name, email, text) VALUES ('0','exemplo de título', 'lucas', 'lucas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('1','exemplo de título', 'lucas', 'lducas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('2','exemplo de título', 'lucas', 'lucdas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('3','exemplo de título', 'lucas', 'lucfas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('4','exemplo de título', 'lucas', 'lucass@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('5','exemplo de título', 'lucas', 'lucfas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('6','exemplo de título', 'lucas', 'lucvas@usp.br', 'texto exemplo');
INSERT INTO notes (tag, title, name, email, text) VALUES ('7','exemplo de título', 'lucas', 'lucbas@usp.br', 'texto exemplo');
