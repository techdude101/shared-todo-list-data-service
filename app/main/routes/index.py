from flask import Blueprint
from app import version

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    """Handles the index route

    Returns:
        Response: A Flask response object containing the JSON data.
    """
    response = {
        "version": version
    }
    return response
