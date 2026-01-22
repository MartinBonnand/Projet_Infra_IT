DROP TABLE IF EXISTS taches;

CREATE TABLE taches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    date_echeance DATE,
    terminee INTEGER DEFAULT 0
);
