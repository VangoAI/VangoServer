import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class RequestManager:
    def __init__(self):
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    def get_google_user(self, auth_code: str) -> tuple[str, str, str]:
        '''
        Given an authorization code, returns the user's google ID, email, and name.
        '''
        url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{os.getenv('BACKEND_BASE_URL')}/api/auth/google/callback"

        payload = {
            "code": auth_code,
            "client_id": self.GOOGLE_CLIENT_ID,
            "client_secret": self.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, data=payload, headers=headers)
        response_data = response.json()

        idinfo = id_token.verify_oauth2_token(response_data["id_token"], google_requests.Request(), self.GOOGLE_CLIENT_ID)
        return idinfo["sub"], idinfo["email"], idinfo["name"]
