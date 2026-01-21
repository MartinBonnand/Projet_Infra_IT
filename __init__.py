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

# --- AUTHENTIFICATION ---
def est_admin(): return session.get('authentifie')
def est_user(): return session.get('user_authentifie')

@app.route('/')
def index():
    return render_template('hello.html')

# --- GESTION DES LIVRES ---

@app.route('/biblio')
def consultation_livres():
    conn = get_db_connection()
    livres = conn.execute('SELECT * FROM livres').fetchall()
    conn.close()
    return render_template('read_data.html', data=livres)

@app.route('/biblio/disponibles')
def livres_dispo():
    conn = get_db_connection()
    livres = conn.execute('SELECT * FROM livres WHERE stock > 0').fetchall()
    conn.close()
    return render_template('read_data.html', data=livres)

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
    return redirect(url_for('consultation_livres'))

# --- ADMINISTRATION (AJOUT / SUPPRESSION) ---

@app.route('/admin/supprimer/<int:livre_id>')
def supprimer_livre(livre_id):
    if not est_admin():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('consultation_livres'))

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
        return redirect(url_for('consultation_livres'))
    
    return '''
        <form method="post">
            Titre: <input name="titre"><br> Auteur: <input name="auteur"><br> Stock: <input name="stock"><br>
            <input type="submit" value="Ajouter">
        </form>
    '''

# --- LOGIN / LOGOUT ---

@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        # On essaie de récupérer 'username' OU 'login' au cas où
        username_saisi = request.form.get('username') or request.form.get('login')
        password_saisi = request.form.get('password')

        if username_saisi == 'user' and password_saisi == '12345':
            session['user_authentifie'] = True
            # Redirige vers la bibliothèque après connexion
            return redirect(url_for('liste_livres')) 
        else:
            # Si ça échoue, on affiche l'erreur sur le formulaire
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

# --- ROUTE 1 : VOIR TOUS LES EMPRUNTS (ADMIN) ---
@app.route('/admin/emprunts')
def voir_emprunts():
    if not session.get('authentifie'): # Sécurité Admin
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    # On fait une jointure pour avoir le titre du livre dans le tableau des emprunts
    query = '''
        SELECT emprunts.id, livres.titre, emprunts.utilisateur, emprunts.date_emprunt 
        FROM emprunts 
        JOIN livres ON emprunts.livre_id = livres.id
    '''
    emprunts = conn.execute(query).fetchall()
    conn.close()
    return render_template('bibliotheque.html', emprunts=emprunts, mode='admin_emprunts')

# --- ROUTE 2 : SUPPRIMER UN LIVRE (ADMIN) ---
@app.route('/admin/supprimer_livre/<int:livre_id>')
def supprimer_livre_v2(livre_id):
    if not session.get('authentifie'):
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('liste_livres'))

# --- ROUTE 3 : INTERFACE PRINCIPALE (BIBLIOTHÈQUE) ---
@app.route('/bibliotheque')
def liste_livres():
    conn = get_db_connection()
    livres = conn.execute('SELECT * FROM livres').fetchall()
    conn.close()
    return render_template('bibliotheque.html', livres=livres, mode='liste')
