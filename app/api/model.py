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
        model = data_manager.complete_upload(user_id, request.json['model_id'], request.json['name'], request.json['upload_id'], request.json['parts'])
    except Exception as e:
        return {"error completing upload": str(e)}, 500
    return model, 200
