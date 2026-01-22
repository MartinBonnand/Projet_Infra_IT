DROP TABLE IF EXISTS taches;
DROP TABLE IF EXISTS livres;
DROP TABLE IF EXISTS emprunts;
DROP TABLE IF EXISTS clients;

CREATE TABLE taches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    date_echeance DATE,
    terminee INTEGER DEFAULT 0
);
