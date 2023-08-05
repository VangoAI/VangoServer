from dotenv import load_dotenv
load_dotenv()
from flask import Flask, Blueprint
from flask_cors import CORS

from app.api.auth import auth
from app.services.data_manager import DataManager
from app.services.request_manager import RequestManager

app = Flask(__name__)
CORS(app)

app.data_manager = DataManager()
app.request_manager = RequestManager()

api = Blueprint('api', __name__)
api.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
