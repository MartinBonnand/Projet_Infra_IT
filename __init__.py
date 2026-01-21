from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# ==========================
# Fonctions d'authentification
# ==========================

# Admin
def est_authentifie():
    return session.get('authentifie')

# User
def est_authentifie_user():
    return session.get('user_authentifie')


# ==========================
# Routes principales
# ==========================

@app.route('/')
def hello_world():
    return render_template('hello.html')


@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié (ADMIN)</h2>"


# ==========================
# Authentification ADMIN
# ==========================

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


# ==========================
# Authentification USER
# ==========================

@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '12345':
            session['user_authentifie'] = True
            return redirect(url_for('fiche_nom_form'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


# ==========================
# Recherche client par NOM
# ==========================

@app.route('/fiche_nom')
def fiche_nom_form():
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    return '''
        <h2>Recherche client par nom</h2>
        <form method="post" action="/fiche_nom_resultat">
            Nom : <input type="text" name="nom" required>
            <input type="submit" value="Rechercher">
        </form>
    '''


@app.route('/fiche_nom_resultat', methods=['POST'])
def fiche_nom_resultat():
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    nom = request.form['nom']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return "<h3>Aucun client trouvé</h3>"

    return render_template('read_data.html', data=data)


# ==========================
# Consultation par ID (existant)
# ==========================

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


# ==========================
# Enregistrement client
# ==========================

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')


@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)',
        (1002938, nom, prenom, "ICI")
    )
    conn.commit()
    conn.close()

    return redirect('/consultation/')


# ==========================
# Déconnexion USER
# ==========================

@app.route('/logout_user')
def logout_user():
    session.pop('user_authentifie', None)
    return redirect('/')


# ==========================
# Lancement application
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
