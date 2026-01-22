from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Configuration du chemin de la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- ACCUEIL ---
@app.route('/')
def index():
    # Page d'accueil avec navigation vers les fonctionnalités 
    return render_template('index.html')

# --- AFFICHER LES TÂCHES ---
@app.route('/taches')
def liste_taches():
    conn = get_db_connection()
    # Récupère les tâches (Liste visible avec titre et description )
    taches = conn.execute('SELECT * FROM taches ORDER BY date_echeance ASC').fetchall()
    conn.close()
    return render_template('taches.html', taches=taches)

# --- AJOUTER UNE TÂCHE ---
@app.route('/taches/ajouter', methods=['GET', 'POST'])
def ajouter_tache():
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        date_echeance = request.form['date_echeance'] # 
        
        conn = get_db_connection()
        conn.execute('INSERT INTO taches (titre, description, date_echeance) VALUES (?, ?, ?)',
                     (titre, description, date_echeance))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_taches'))
    return render_template('formulaire.html')

# --- MARQUER COMME TERMINÉE ---
@app.route('/taches/terminer/<int:id>')
def terminer_tache(id):
    conn = get_db_connection()
    # Permettre de marquer une tâche comme terminée 
    conn.execute('UPDATE taches SET terminee = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('liste_taches'))

# --- SUPPRIMER UNE TÂCHE ---
@app.route('/taches/supprimer/<int:id>')
def supprimer_tache(id):
    conn = get_db_connection()
    # Permettre la suppression d'une tâche 
    conn.execute('DELETE FROM taches WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('liste_taches'))

if __name__ == "__main__":
    app.run(debug=True)
