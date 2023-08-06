import os
from flask import current_app, Blueprint, request, redirect, make_response
from urllib.parse import urlencode
from app.utils import generate_token, token_required

auth = Blueprint('auth', __name__)

@auth.route('/check')
@token_required
def check(user_id):
    return '', 200

@auth.route('/google/login')
def google_auth():
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": "http://localhost:5000/api/auth/google/callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
    }
    return redirect(f"{authorization_url}?{urlencode(params)}")

@auth.route('/google/callback')
def google_auth_callback():
    data_manager = current_app.data_manager
    request_manager = current_app.request_manager

    auth_code = request.args.get('code')

    google_id, email, name = request_manager.get_google_user(auth_code)
    user = data_manager.get_user_from_google_id(google_id) if data_manager.google_id_exists(google_id) else data_manager.create_user(google_id, email, name)
    token = generate_token(user['user_id'])
    response = make_response(redirect(f"{os.getenv('FRONTEND_BASE_URL')}/"))
    response.set_cookie('token', token, httponly=True)
    return response

@auth.route('/logout')
@token_required
def logout(user_id):
    response = make_response(redirect(f"{os.getenv('FRONTEND_BASE_URL')}/"))
    response.delete_cookie('token') # could add to a blacklist but whatever
    return response
