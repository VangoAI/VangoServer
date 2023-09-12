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

import os
from dotenv import load_dotenv
load_dotenv()
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
        DREAMLOOK_API_KEY = os.getenv('DREAMLOOK_API_KEY')

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
            "extract_lora": "disabled",
            "text_encoder_training": {
                "steps": 2400,
                "learning_rate": 0.00001
            }
        }
        import requests
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        train_jobs[response.json()['job_id']] = (user_id, model_name)

    except Exception as e:
        return {"error training dreambooth": str(e)}, 500
    return "", 200

@model.route('/train/dreambooth/complete', methods=['POST'])
def complete_train_dreambooth():
    data_manager = current_app.data_manager
    try:
        job_id = request.json['job_id']
        model_url = request.json['dreambooth_result']['checkpoints'][0]['url']
        user_id, model_name = train_jobs.get(job_id, (None, None))
        print(user_id, model_name, model_url, job_id)
        import boto3
        import uuid
        import requests
        s3 = boto3.client('s3', region_name='us-west-2', 
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

        try:
            from contextlib import closing
            model_id = str(uuid.uuid4())
            print("model id", model_id)
            with closing(requests.get(model_url, stream=True)) as r:
                print("uploading to s3")
                s3.upload_fileobj(r.raw, "vango-models", model_id)
        except Exception as e:
            print("error uploading to s3", str(e))
            return {"error uploading to s3": str(e)}, 500
        s3_url = f"https://vango-models.s3-us-west-2.amazonaws.com/{model_id}"
        model = data_manager.create_model(user_id, model_name, 'Checkpoint', s3_url, model_id)
    except Exception as e:
        return {"error training dreambooth": str(e)}, 500
    return model, 200
