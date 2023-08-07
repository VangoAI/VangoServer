from flask import current_app, Blueprint
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
