from flask import current_app, Blueprint, request
from app.utils import token_required

model = Blueprint('model', __name__)


@model.route('/list')
@token_required
def list_models(user_id):
    data_manager = current_app.data_manager
    try:
        models = data_manager.list_models(user_id)
    except Exception as e:
        return {"error listing models": str(e)}, 500
    return models, 200

@model.route('/upload/start', methods=['POST'])
@token_required
def start_upload(user_id):
    data_manager = current_app.data_manager
    try:
        model_id, upload_id, presigned_urls = data_manager.start_upload(request.json['num_parts'])
    except Exception as e:
        return {"error getting presigned urls": str(e)}, 500
    return {"model_id": model_id, "upload_id": upload_id, "presigned_urls": presigned_urls}, 200

@model.route('/upload/complete', methods=['POST'])
@token_required
def complete_upload(user_id):
    data_manager = current_app.data_manager
    try:
        model = data_manager.complete_upload(user_id, request.json['model_id'], request.json['name'], request.json['type'], request.json['upload_id'], request.json['parts'])
    except Exception as e:
        return {"error completing upload": str(e)}, 500
    return model, 200

train_jobs = {}

@model.route('/train/dreambooth/start', methods=['POST'])
@token_required
def start_train_dreambooth(user_id):
    try:
        model_name = request.json['model_name']
        instance_prompt = request.json['instance_prompt']
        liked_images = request.json['liked_images']
        print(model_name, instance_prompt, liked_images)

        url = 'https://api.dreamlook.ai/dreambooth'
        DREAMLOOK_API_KEY = "dl-418252CBBEDD464C8BA6B79258FF2E0C"

        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer {}'.format(DREAMLOOK_API_KEY)
        }

        data = {
            "image_urls": liked_images,
            "steps": 2400,
            "learning_rate": 0.00001,
            "instance_prompt": instance_prompt,
            "model_type": "sdxl-v1",
            "base_model": "stable-diffusion-xl-v1-0",
            "crop_method": "center",
            "saved_model_format": "original",
            "saved_model_weights_format": "safetensors",
            "callback": "https://vango.ai/api/model/train/dreambooth/complete",
            "dry_run": True,
            "extract_lora": "disabled",
            "text_encoder_training": {
                "steps": 2400,
                "learning_rate": 0.00001
            }
        }
        import requests
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        train_jobs[response.json()['job_id']] = model_name

    except Exception as e:
        return {"error training dreambooth": str(e)}, 500
    return "", 200

@model.route('/train/dreambooth/complete', methods=['POST'])
def complete_train_dreambooth(user_id):
    data_manager = current_app.data_manager
    try:
        print('recieved callback')
        print(request.json)
    except Exception as e:
        return {"error training dreambooth": str(e)}, 500
    return model, 200
