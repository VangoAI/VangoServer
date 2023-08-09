import requests
from flask import current_app, Blueprint, request, redirect, make_response
from urllib.parse import urlencode
from app.utils import  token_required

comfy = Blueprint('comfy', __name__)

# TODO: make sure the api request is only done when the user is authenticated
@comfy.route('/load')
@token_required
def load_comfyui():
    # request should include the user's S3 shit
    
    
    potential_comfyuis = [
        "http://logo.vango.ai:8188/",
        "http://logo.vango.ai:8189/",
        "http://logo.vango.ai:8190/",
        "http://logo.vango.ai:8191/"
    ]

    def get_num_queue(url):
        response = requests.get(f"{url}/queue")
        return len(response.json()['queue_pending']) + len(response.json()['queue_running'])

    free_comfyui_url = min(potential_comfyuis, key = get_num_queue)

    return free_comfyui_url