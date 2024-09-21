from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'development'

# Configurando OAuth
oauth = OAuth(app)
oauth.register(
    name='suap',
    client_id='',  # Carrega do ambiente
    client_secret='',  # Carrega do ambiente
    api_base_url='https://suap.ifrn.edu.br/api/',
    access_token_method='POST',
    access_token_url='https://suap.ifrn.edu.br/o/token/',
    authorize_url='https://suap.ifrn.edu.br/o/authorize/',
    fetch_token=lambda: session.get('suap_token')
)

@app.route("/")
def index():
    """Página inicial, redireciona para o perfil se já autenticado."""
    if "suap_token" in session:
        profile_data = fetch_profile_data()
        return render_template("index.html", profile_data=profile_data)
    return render_template("login.html")

@app.route("/login")
def login():
    """Inicia o processo de login."""
    redirect_uri = url_for('auth', _external=True)
    return oauth.suap.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    """Desconecta o usuário, removendo o token da sessão."""
    session.pop('suap_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def auth():
    """Recebe o callback após a autorização e armazena o token na sessão."""
    try:
        token = oauth.suap.authorize_access_token()
        session['suap_token'] = token
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Authorization error: {e}")
        return redirect(url_for('index'))

@app.route("/profile")
def profile():
    """Exibe o perfil do usuário."""
    if "suap_token" in session:
        profile_data = fetch_profile_data()
        return render_template("profile.html", profile_data=profile_data)
    return redirect(url_for('index'))

@app.route("/formulario", methods=["GET", "POST"])
def grades():  # Mudado para grades
    """Exibe as notas do usuário com base no ano e semestre."""
    if "suap_token" in session:
        year = request.args.get("school_year", datetime.now().year)
        semester = request.args.get("semester", '1')  # Garanta que o semestre seja uma string
        profile_data = fetch_profile_data()
        grades_data = fetch_grades_data(year, semester)
        
        return render_template("grades.html",  # Mudado para grades.html
                               grades_data=grades_data,
                               profile_data=profile_data,
                               year=year,
                               semester=semester)
    return redirect(url_for('index'))

def fetch_profile_data():
    """Recupera dados do perfil do usuário da API."""
    response = oauth.suap.get("v2/minhas-informacoes/meus-dados")
    return response.json() if response.ok else {}

def fetch_grades_data(year, semester):
    """Recupera as notas do usuário da API."""
    try:
        grades_response = oauth.suap.get(f"v2/minhas-informacoes/boletim/{year}/{semester}/")
        grades_response.raise_for_status()  # Levanta um erro se a resposta não for 200 OK
        return grades_response.json()
    except Exception as e:
        print(f"Error fetching grades: {e}")
        return []  # Retorna lista vazia em caso de erro

if __name__ == "__main__":
    app.run(debug=True)