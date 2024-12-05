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
from werkzeug.sansio.response import Response
from app.main.request_log_formatter import RequestFormatter


version = "1.2.3"


# Application Factory #
def create_app() -> Flask:
    """Create the Flask application.

    Returns:
        Flask: a flask object
    """

    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})

    # Register blueprints
    register_blueprints(app)

    # Configure logging
    configure_logging(app)

    # Register error handlers
    register_error_handlers(app)

    return app


# Helper Functions #
def register_blueprints(app: Flask):
    """Register blueprints on the flask application.

    Args:
        app (Flask): flask application
    """

    from app.main.routes.index import main_blueprint
    from app.main.routes.todos import todos_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(todos_blueprint)


def register_error_handlers(app: Flask):
    """Register error handlers on the flask application.

    Args:
        app (Flask): flask application

    Returns:
        None: no return
    """

    @app.errorhandler(HTTPException)
    def handle_exception(e: HTTPException) -> Response:
        """Return JSON instead of HTML for HTTP errors.

        Args:
            e (HTTPException): HTTP exception

        Returns:
            Response: the response
        """
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "message": e.description,
        })
        response.content_type = "application/json"
        return response


def configure_logging(app: Flask):
    """Configure logging for the flask application.

    Args:
        app (Flask): flask application
    """

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
