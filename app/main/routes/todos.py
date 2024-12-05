from flask import current_app, request, Blueprint
from werkzeug.exceptions import (
  BadRequest, NotFound, InternalServerError, Conflict
)
from pydantic import ValidationError
from mysql.connector.errors import DatabaseError
from mysql.connector import MySQLConnection
from app.models.todo_item import TodoItem
from app.main.decorators.db_connection import get_db_connection
from app.main.database import call_stored_procedure, check_todo_exists
from app.main.constants.en.response_messages import INTERNAL_SERVER_ERROR

todos_blueprint = Blueprint('todos', __name__)


@todos_blueprint.route('/todos/<user_id>', methods=['GET'])
@get_db_connection
def get_todos(db_connection: MySQLConnection,
              user_id: int):
    """Endpoint to handle retrieving a list of to-do items.

    Args:
        db_connection (MySQLConnection): MySQL database connection
        user_id (int): the user ID

    Returns:
        Response: A Flask response object containing the JSON data.
    """

    current_app.logger.info("get to-dos for user id: %s", user_id)

    try:
        user_id_int = int(user_id)
        if user_id_int < 1:
            raise ValueError("User ID must be greater than 0")

        db_cursor = db_connection.cursor()
        db_cursor.execute("""CALL get_todos_for_user_id((%s))""", (user_id,))
        todos_result = db_cursor.fetchall()

        todos = []

        for todo in todos_result:
            todos.append(TodoItem(id=todo[0], data=todo[1],
                                  completed=todo[2],
                                  completed_timestamp=todo[3]).model_dump())
        current_app.logger.debug(todos)
        return todos
    except ValueError as ve:
        current_app.logger.exception(ve)
        raise BadRequest()
    except DatabaseError as db_error:
        current_app.logger.exception(db_error)
        raise InternalServerError()


@todos_blueprint.route('/todos/<user_id>', methods=['POST'])
@get_db_connection
def add_todo(db_connection: MySQLConnection,
             user_id: int):
    """Endpoint to handle adding a new to-do item.

    Args:
        db_connection (MySQLConnection): MySQL database connection
        user_id (int): the user ID

    Returns:
        Response: A Flask response object containing the JSON data.
    """

    current_app.logger.info("add to-do for user id: %s", user_id)

    # Check if user is allowed to perform this operation
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.get_json()
        current_app.logger.info("add to-do: %s", json)

        try:
            TodoItem.model_validate(json)
            user_id_int = int(user_id)
            todo_id_int = int(json["id"])

            todo_exists = check_todo_exists(db_connection,
                                            user_id_int, todo_id_int)
            if todo_exists:
                raise Conflict()

            args = (int(user_id),
                    json["id"],
                    json["data"],
                    json["completed"])

            result = call_stored_procedure(db_connection,
                                           "add_todo_for_user_id",
                                           args)
            current_app.logger.debug(f"Add to DB result: {result}")

            return json
        except KeyError as ke:
            current_app.logger.warning("Invalid todo payload %s", json)
            current_app.logger.exception(ke)
            raise BadRequest()
        except ValidationError as ve:
            current_app.logger.warning("Invalid todo payload %s", json)
            current_app.logger.exception(ve)
            raise BadRequest()
        except TypeError as te:
            current_app.logger.warning("Invalid todo payload %s", json)
            current_app.logger.exception(te)
            raise BadRequest()
        except DatabaseError as db_error:
            current_app.logger.exception(db_error)
            if db_error.errno == 1644:
                raise Conflict()
            raise InternalServerError(INTERNAL_SERVER_ERROR)
    else:
        raise BadRequest()


@todos_blueprint.route('/todos/<user_id>/<todo_id>', methods=['PUT'])
@get_db_connection
def update_todo(db_connection: MySQLConnection,
                user_id: int, todo_id: int):
    """Endpoint to handle updating a to-do item.

    Args:
        db_connection (MySQLConnection): MySQL database connection
        user_id (int): the user ID
        todo_id (int): the ID of the to-do item

    Returns:
        Response: A Flask response object containing the JSON data.
    """
    # Check if user is allowed to perform this operation
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json_body = request.get_json()

        try:
            user_id_int = int(user_id)
            todo_id_int = int(todo_id)
            json_body["id"] = todo_id_int

            todo_exists = check_todo_exists(db_connection,
                                            user_id_int, todo_id_int)

            if not todo_exists:
                raise NotFound()

            current_app.logger.info("update to-do: %s", json_body)

            TodoItem.model_validate(json_body)

            current_app.logger.info("update to-do: %s", json_body)
            args = (int(user_id),
                    int(todo_id),
                    json_body["data"],
                    json_body["completed"],
                    json_body["completed_timestamp"])
            result = call_stored_procedure(
                db_connection,
                "update_todo_for_user_id",
                args)
            current_app.logger.debug(f"Update DB result: {result}")
            return json_body

        except ValueError as ve:
            current_app.logger.exception(ve)
            raise BadRequest()
        except ValidationError as ve:
            current_app.logger.warning("Invalid todo payload %s", json_body)
            current_app.logger.exception(ve)
            raise BadRequest()
        except DatabaseError as de:
            current_app.logger.exception(de)
            raise BadRequest()
    else:
        raise BadRequest()


@todos_blueprint.route('/todos/<user_id>/<todo_id>', methods=['DELETE'])
@get_db_connection
def delete_todo(db_connection: MySQLConnection,
                user_id: int, todo_id: int):
    """Endpoint to handle deleting a to-do item.

    Args:
        db_connection (MySQLConnection): MySQL database connection
        user_id (int): the user ID
        todo_id (int): the ID of the to-do item

    Returns:
        Response: A Flask response object containing the JSON data.
    """
    # Check if user is allowed to perform this operation
    # Security: rate limiting + ask for user credentials for this operation

    current_app.logger.info("delete to-do: %s", todo_id)

    try:
        user_id_int = int(user_id)
        todo_id_int = int(todo_id)

        todo_exists = check_todo_exists(db_connection,
                                        user_id_int, todo_id_int)
        args = (user_id_int, todo_id_int)

        if not todo_exists:
            raise NotFound()
        call_stored_procedure(
                db_connection,
                "delete_todo_for_user_id",
                args)
    except ValueError as ve:
        current_app.logger.exception(ve)
        raise BadRequest()
    except DatabaseError as de:
        current_app.logger.exception(de)
        raise BadRequest()

    return '', 204
