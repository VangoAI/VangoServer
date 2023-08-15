from flask import current_app, Blueprint, request
from app.utils import token_required

file = Blueprint('file', __name__)

@file.route('/create', methods=['POST'])
@token_required
def create_file(user_id):
    data_manager = current_app.data_manager
    try:
        file = data_manager.create_file(user_id)
    except Exception as e:
        return {"error creating file": str(e)}, 500
    return file, 201

@file.route('/<string:file_id>')
@token_required
def get_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        file = data_manager.get_file(file_id)
    except Exception as e:
        return {"error getting file": str(e)}, 500

    if not file:
        return '', 404
    return file, 200

@file.route('/<string:file_id>/content')
@token_required
def get_file_content(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        content = data_manager.get_file_content(file_id)
    except Exception as e:
        return {"error getting file content": str(e)}, 500

    return content, 200

@file.route('/<string:file_id>/save', methods=['POST'])
@token_required
def save_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        data_manager.save_file(file_id, request.json['content'])
    except Exception as e:
        return {"error saving file": str(e)}, 500
    return '', 204

@file.route('/<string:file_id>/delete', methods=['DELETE'])
@token_required
def delete_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        data_manager.delete_file(file_id)
    except Exception as e:
        return {"error deleting file": str(e)}, 500
    return '', 204

@file.route('/list')
@token_required
def list_files(user_id):
    data_manager = current_app.data_manager
    try:
        files = data_manager.get_files(user_id)
    except Exception as e:
        return {"error listing files": str(e)}, 500
    return files, 200

@file.route('/<string:file_id>/rename', methods=['POST'])
@token_required
def rename_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        file = data_manager.rename_file(file_id, request.json['file_name'])
    except Exception as e:
        return {"error renaming file": str(e)}, 500
    return file, 200

@file.route('/<string:file_id>/copy', methods=['POST'])
@token_required
def copy_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        file = data_manager.copy_file(user_id, file_id)
    except Exception as e:
        return {"error copying file": str(e)}, 500
    return file, 201

@file.route('/images')
def get_images():
    data_manager = current_app.data_manager
    return data_manager.get_images(), 200
