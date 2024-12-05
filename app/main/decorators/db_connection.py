import logging
from functools import wraps
from app.main.database import get_database_connection
from werkzeug.exceptions import HTTPException


def get_db_connection(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            db_connection = get_database_connection()
            kwargs["db_connection"] = db_connection
            return f(*args, **kwargs)
        except Exception as ex:
            if not isinstance(ex, HTTPException):
                logging.exception(ex)
            return f(*args, **kwargs)
    return wrapper
