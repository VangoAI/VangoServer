import os
import datetime
from functools import wraps

from flask import request, jsonify
import jwt
import requests

def token_required(f):
    """
    Decorator that checks if a valid token is present in the request cookies.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        user_id = decode_token(token)
        return f(user_id, *args, **kwargs)

    return decorator

def generate_token(user_id: str) -> str:
    """
    Generate a jwt for the given user ID.

    Args:
        user_id (str): The ID of the user for whom the token is being generated.

    Returns:
        str: The generated token.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

def decode_token(token: str) -> str | None:
    """
    Decodes a jwt and returns the user ID contained inside.

    Args:
        token (str): The token to be decoded.

    Returns:
        str | None: The user ID if the token is valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return jsonify({'message': 'Token is invalid!'}), 401


def upload_in_chunks(url, file):
    chunk_size = 1024 * 1024 * 10
    file_stream = file.stream

    while True:
        chunk_data = file_stream.read(chunk_size)
        if len(chunk_data) == 0:
            break
            
        files = {'file': (file.filename, chunk_data, file.mimetype)}
        response = requests.post(url, files=files)
        
        if response.status_code != 200:
            return f'Failed to upload chunk, status code: {response.status_code}', 400
            
    return 'File successfully uploaded', 200
