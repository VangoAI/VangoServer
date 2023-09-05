from flask import current_app, Blueprint, request
from app.utils import token_required

user = Blueprint('user', __name__)

@user.route('/<string:id>')
@token_required
def get_user(user_id, id):
    data_manager = current_app.data_manager
    try:
        user = data_manager.get_user(id)
    except Exception as e:
        return {"error getting user": str(e)}, 500

    if not user:
        return '', 404
    return user, 200

@user.route('/usernames', methods=['POST'])
@token_required
def get_usernames(user_id):
    data_manager = current_app.data_manager
    try:
        usernames = data_manager.get_usernames(request.json['user_ids'])
    except Exception as e:
        print("error", e)
        return {"error getting usernames": str(e)}, 500
    return usernames, 200
