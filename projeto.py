import requests

def get_access_token(code):
    token_url = 'https://suap.ifrn.edu.br/accounts/login/'
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    redirect_uri = 'YOUR_REDIRECT_URI'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, data=data)
    return response.json()['access_token']

from flask import Flask, request, redirect, session, url_for, render_template
import requests

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = 'YOUR_REDIRECT_URI'

@app.route('/')
def home():
    if 'access_token' in session:
        return redirect(url_for('profile'))
    return 'Welcome! <a href="/login">Login with SUAP</a>'

@app.route('/login')
def login():
    authorization_url = f'https://suap.gov.br/oauth/authorize/?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}'
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token = get_access_token(code)
    session['access_token'] = token
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('home'))
    
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info = requests.get('https://suap.gov.br/api/v2/minhas-informacoes/', headers=headers).json()
    user_photo = user_info.get('foto')
    user_name = user_info.get('nome')
    return render_template('profile.html', name=user_name, photo=user_photo)

@app.route('/boletins', methods=['GET'])
def boletins():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('home'))

    ano = request.args.get('ano')
    semestre = request.args.get('semestre')

    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'ano': ano, 'semestre': semestre}
    boletins_response = requests.get('https://suap.gov.br/api/v2/boletins/', headers=headers, params=params)
    boletins = boletins_response.json()
    return render_template('boletins.html', boletins=boletins)

def get_access_token(code):
    token_url = 'https://suap.gov.br/oauth/token/'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(token_url, data=data)
    return response.json()['access_token']

if __name__ == '__main__':
    app.run(debug=True)

