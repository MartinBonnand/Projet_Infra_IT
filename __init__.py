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

# --- HELPERS ---
def est_admin(): return session.get('authentifie')
def est_user(): return session.get('user_authentifie')

@app.route('/')
def index():
    return render_template('hello.html')

# --- AUTHENTIFICATION ADMIN ---
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':
            session['authentifie'] = True
            return redirect(url_for('index'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html')

# --- AUTHENTIFICATION USER ---
@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        username = request.form.get('username') or request.form.get('login')
        password = request.form.get('password')
        if username == 'user' and password == '12345':
            session['user_authentifie'] = True
            return redirect(url_for('liste_livres')) 
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html')

# --- LOGOUT ---
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
    return render_template('bibliotheque.html', livres=livres, mode='liste')

@app.route('/biblio/emprunter/<int:livre_id>')
def emprunter(livre_id):
    if not est_user():
        return redirect(url_for('authentification_user'))
    
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
        conn = get_db_connection()
        conn.execute('INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)', (titre, auteur, stock))
        conn.commit()
        conn.close()
        return redirect(url_for('liste_livres'))
    
    return '''
        <form method="post">
            Titre: <input name="titre"><br> Auteur: <input name="auteur"><br> Stock: <input name="stock"><br>
            <input type="submit" value="Ajouter">
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
