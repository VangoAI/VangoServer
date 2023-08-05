import os

from dotenv import load_dotenv
load_dotenv()
from flask import Flask, Blueprint, jsonify, request, redirect, make_response
from urllib.parse import urlencode
from flask_cors import CORS

from data_manager import DataManager
from request_manager import RequestManager
from utils import generate_token

app = Flask(__name__)
CORS(app)

data_manager = DataManager()
request_manager = RequestManager()

@app.route('/api/auth/google/login')
def google_auth():
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": "842755270822-bqnknh0ot4iocuigvlprm79vf9m1s84t.apps.googleusercontent.com",
        "redirect_uri": "http://localhost:5000/api/auth/google/callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
    }
    return redirect(f"{authorization_url}?{urlencode(params)}")

@app.route('/api/auth/google/callback')
def google_auth_callback():
    auth_code = request.args.get('code')

    google_id, email, name = request_manager.get_google_user(auth_code)
    user = data_manager.get_user_from_google_id(google_id) if data_manager.google_id_exists(google_id) else data_manager.create_user(google_id, email, name)
    token = generate_token(user['user_id'])

    response = make_response(redirect(f"{os.getenv('FRONTEND_BASE_URL')}/dashboard"))
    response.set_cookie('token', token, httponly=True)
    return response

if __name__ == '__main__':
    app.run(debug=True)
