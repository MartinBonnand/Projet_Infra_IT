from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Utiliser un chemin absolu pour la base de données sur Alwaysdata
# Cela évite les erreurs où SQLite ne trouve pas le fichier .db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- AUTHENTIFICATION ---

def est_authentifie():
    return session.get('authentifie')

def est_authentifie_user():
    return session.get('user_authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

# --- SEQUENCE 5 : AUTHENTIFICATION USER (user / 12345) ---

@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        # On vérifie 'username' car c'est souvent le nom dans le HTML
        login = request.form.get('username') or request.form.get('login')
        password = request.form.get('password')

        if login == "user" and password == "12345":
            session['user_authentifie'] = True
            return redirect(url_for('fiche_nom'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

# --- SEQUENCE 5 : RECHERCHE PAR NOM ---

# Ajout de strict_slashes=False pour éviter l'erreur 404 si tu ajoutes un / à la fin
@app.route('/fiche_nom/', strict_slashes=False)
def fiche_nom():
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))
    
    # Formulaire simple en HTML pour la recherche
    return '''
        <html>
            <body>
                <h2>Recherche de client par nom</h2>
                <form action="/recherche_resultat" method="GET">
                    Nom : <input type="text" name="nom_client">
                    <input type="submit" value="Chercher">
                </form>
                <br><a href="/logout_user">Se déconnecter</a>
            </body>
        </html>
    '''

@app.route('/recherche_resultat')
def recherche_resultat():
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    nom_recherche = request.args.get('nom_client')
    
    conn = get_db_connection()
    # Utilisation de LIKE pour être plus souple (trouve "Dupont" même si on tape "dupont")
    cursor = conn.execute('SELECT * FROM clients WHERE nom LIKE ?', (nom_recherche,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return f"<h3>Aucun client trouvé pour le nom : {nom_recherche}</h3><a href='/fiche_nom'>Retour</a>"

    return render_template('read_data.html', data=data)

# --- ROUTES ADMIN EXISTANTES ---

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        login = request.form.get('username') or request.form.get('login')
        password = request.form.get('password')
        if login == 'admin' and password == 'password':
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié en tant qu'ADMIN</h2>"

@app.route('/consultation/')
def ReadBDD():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM clients;').fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/logout_user')
def logout_user():
    session.pop('user_authentifie', None)
    return redirect(url_for('hello_world'))

if __name__ == "__main__":
    app.run(debug=True)
