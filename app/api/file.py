import os
from flask import current_app, Blueprint, request, redirect, make_response
from urllib.parse import urlencode
from app.utils import token_required

file = Blueprint('file', __name__)

@file.route('/create', methods=['POST'])
@token_required
def create_file(user_id):
    data_manager = current_app.data_manager
    try:
        data_manager.create_file(user_id)
    except Exception as e:
        return {"error creating file": str(e)}, 500
    return None, 201

@file.route('/get/<string:file_id>')
@token_required
def get_file(user_id, file_id):
    data_manager = current_app.data_manager

    try:
        file = data_manager.get_file(file_id)
    except Exception as e:
        return {"error getting file": str(e)}, 500

    if not file:
        return None, 404
    return file, 200

@file.route('/save/<string:file_id>', methods=['POST'])
@token_required
def save_file(user_id, file_id):    
    data_manager = current_app.data_manager
    try:
        data_manager.save_file(file_id, request.json['content'])
    except Exception as e:
        return {"error saving file": str(e)}, 500
    return None, 204

@file.route('/delete/<string:file_id>', methods=['DELETE'])
@token_required
def delete_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        data_manager.delete_file(file_id)
    except Exception as e:
        return {"error deleting file": str(e)}, 500
    return None, 204

@file.route('/list')
@token_required
def list_files(user_id):
    data_manager = current_app.data_manager
    try:
        files = data_manager.get_files(user_id)
    except Exception as e:
        return {"error listing files": str(e)}, 500
    return files, 200

@file.route('/rename/<string:file_id>', methods=['POST'])
@token_required
def rename_file(user_id, file_id):
    data_manager = current_app.data_manager
    try:
        data_manager.rename_file(file_id, request.json['file_name'])
    except Exception as e:
        return {"error renaming file": str(e)}, 500
    return None, 204

