from dotenv import load_dotenv
load_dotenv()
from flask import Flask, Blueprint
from flask_cors import CORS

from app.api.auth import auth
from app.api.file import file
from app.api.user import user
from app.api.comfy import comfy
from app.api.other import other
from app.api.experiment import experiment
from app.services.data_manager import DataManager
from app.services.request_manager import RequestManager

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.data_manager = DataManager()
app.request_manager = RequestManager()

api = Blueprint('api', __name__)
api.register_blueprint(auth, url_prefix='/auth')
api.register_blueprint(file, url_prefix='/file')
api.register_blueprint(user, url_prefix='/user')
api.register_blueprint(comfy, url_prefix='/comfy')
api.register_blueprint(other, url_prefix='/other')
api.register_blueprint(experiment, url_prefix='/experiment')

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
