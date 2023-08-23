from flask import current_app, Blueprint, request

other = Blueprint('other', __name__)

@other.route('/images')
def get_images():
    data_manager = current_app.data_manager
    return data_manager.get_images(), 200
