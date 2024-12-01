"""
This contains the application factory for creating flask application instances.
Using the application factory allows for the creation of
flask applications configured for different environments
based on the value of the CONFIG_TYPE environment variable
"""

import os
from flask import Flask, json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from app.main.request_log_formatter import RequestFormatter


# Application Factory #
def create_app():

    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})

    # Configure the flask app instance
    # CONFIG_TYPE = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')  # noqa: E501
    # app.config.from_object(CONFIG_TYPE)

    # Register blueprints
    register_blueprints(app)

    # Configure logging
    configure_logging(app)

    # Register error handlers
    register_error_handlers(app)

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    return app


# Helper Functions #
def register_blueprints(app):
    from app.main.routes.index import main_blueprint
    from app.main.routes.todos import todos_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(todos_blueprint)


def register_error_handlers(app):
    pass


def configure_logging(app):
    import logging

    root = logging.getLogger()
    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    # Create a file handler object
    file_handler = logging.FileHandler('flaskapp.log')

    is_production = os.getenv("IS_PRODUCTION")

    if is_production == "false":
        file_handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)

    # Apply the file formatter object to the file handler object
    file_handler.setFormatter(request_formatter)

    use_wsgi = os.getenv("USE_WSGI")
    if use_wsgi == "true":
        gunicorn_logger = logging.getLogger('gunicorn.error')

        app.logger.addHandler(gunicorn_logger)

    # Add file handler objects to the logger
    app.logger.addHandler(file_handler)
