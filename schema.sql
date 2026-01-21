DROP TABLE IF EXISTS livres;
DROP TABLE IF EXISTS emprunts;

-- Table des livres
CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    stock INTEGER DEFAULT 1,
    disponible BOOLEAN DEFAULT 1
);

-- Table des emprunts pour lier un utilisateur à un livre
CREATE TABLE emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER,
    utilisateur TEXT NOT NULL,
    date_emprunt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (livre_id) REFERENCES livres (id)
);

-- On insère quelques livres pour tester
INSERT INTO livres (titre, auteur, stock) VALUES ('Le Petit Prince', 'Saint-Exupéry', 3);
INSERT INTO livres (titre, auteur, stock) VALUES ('1984', 'George Orwell', 1);
INSERT INTO livres (titre, auteur, stock) VALUES ('Le Seigneur des Anneaux', 'J.R.R. Tolkien', 0);
