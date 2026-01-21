from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- HELPERS (Vérification des rôles) ---
def est_admin():
    return session.get('role') == 'admin'

def est_user():
    return session.get('role') == 'user'

@app.context_processor
def inject_user():
    return dict(role=session.get('role'))

@app.route('/')
def index():
    return render_template('hello.html')

# --- AUTHENTIFICATION UNIQUE (ADMIN & USER) ---
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Cas 1 : Connexion ADMIN
        if username == 'admin' and password == 'password':
            session.clear()
            session['role'] = 'admin'
            return redirect(url_for('liste_livres'))

        # Cas 2 : Connexion USER
        elif username == 'user' and password == '12345':
            session.clear()
            session['role'] = 'user'
            return redirect(url_for('liste_livres'))

        else:
            return render_template('formulaire_authentification.html', error=True)
            
    return render_template('formulaire_authentification.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- GESTION DES LIVRES ---

@app.route('/bibliotheque')
def liste_livres():
    conn = get_db_connection()
    livres = conn.execute('SELECT * FROM livres').fetchall()
    conn.close()
    # On passe le rôle au template pour filtrer les boutons
    return render_template('bibliotheque.html', livres=livres, mode='liste')

@app.route('/biblio/emprunter/<int:livre_id>')
def emprunter(livre_id):
    if not est_user():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    livre = conn.execute('SELECT * FROM livres WHERE id = ?', (livre_id,)).fetchone()
    if livre and livre['stock'] > 0:
        conn.execute('UPDATE livres SET stock = stock - 1 WHERE id = ?', (livre_id,))
        conn.execute('INSERT INTO emprunts (livre_id, utilisateur) VALUES (?, ?)', (livre_id, 'user'))
        conn.commit()
    conn.close()
    return redirect(url_for('liste_livres'))

# --- ADMINISTRATION ---

@app.route('/admin/emprunts')
def voir_emprunts():
    if not est_admin():
        return redirect(url_for('authentification'))
    conn = get_db_connection()
    query = '''
        SELECT emprunts.id, livres.titre, emprunts.utilisateur, emprunts.date_emprunt 
        FROM emprunts 
        JOIN livres ON emprunts.livre_id = livres.id
    '''
    emprunts = conn.execute(query).fetchall()
    conn.close()
    return render_template('bibliotheque.html', emprunts=emprunts, mode='admin_emprunts')

@app.route('/admin/supprimer_livre/<int:livre_id>')
def supprimer_livre_v2(livre_id):
    if not est_admin():
        return redirect(url_for('authentification'))
    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('liste_livres'))

@app.route('/admin/ajouter', methods=['GET', 'POST'])
def ajouter_livre():
    if not est_admin():
        return redirect(url_for('authentification'))
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        stock = request.form['stock']
        conn = get_db_connection
