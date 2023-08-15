from flask import current_app, Blueprint, request
from app.utils import token_required

comfy = Blueprint('comfy', __name__)

@comfy.route('/server')
def get_server():
    return {'api_url': 'https://server1.vango.ai', 'ws_url': 'wss://server1.vango.ai/ws'}, 200
