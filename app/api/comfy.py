from flask import current_app, Blueprint, request
from app.utils import token_required, upload_in_chunks

comfy = Blueprint('comfy', __name__)

API_URL = 'https://server1.vango.ai'
WS_URL = 'wss://server1.vango.ai/ws'

@comfy.route('/server')
@token_required
def get_server(user_id):
    return {'api_url': API_URL, 'ws_url': WS_URL}, 200

@comfy.route('/upload/checkpoint', methods=['POST'])
@token_required
def upload_checkpoint(user_id):
    file = request.files['file']
    upload_url = f'{API_URL}/upload/checkpoint/chunk'
    
    return upload_in_chunks(upload_url, file)

@comfy.route('/upload/lora', methods=['POST'])
@token_required
def upload_lora(user_id):
    file = request.files['file']
    upload_url = f'{API_URL}/upload/lora/chunk'
    
    return upload_in_chunks(upload_url, file)
