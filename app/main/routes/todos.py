from flask import current_app, request, Blueprint
from app.models.todo_item import TodoItem
from pydantic import ValidationError

todos_blueprint = Blueprint('todos', __name__)

todo_list = {"todos": []}


@todos_blueprint.route('/todos/<user_id>', methods=['GET'])
def get_todos(user_id):
    current_app.logger.info("get to-dos for user id: %s", user_id)
    # TODO: Retrieve todos from DB for this user

    return todo_list["todos"]


@todos_blueprint.route('/todos/<user_id>', methods=['POST'])
def add_todo(user_id):
    current_app.logger.info("add to-do for user id: %s", user_id)
    # Check if user is allowed to perform this operation
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        current_app.logger.info("add to-do: %s", json)

        # TODO: Validate then add record to DB
        try:
            TodoItem.model_validate(json)
            todo_list["todos"].append(json)
            return json
        except ValidationError as ve:
            current_app.logger.warning("Invalid todo payload %s", json)
            current_app.logger.exception(ve)
            return {"code": -1, "message": ve.errors()}
        except TypeError as te:
            current_app.logger.warning("Invalid todo payload %s", json)
            current_app.logger.exception(te)
            return {"code": -1, "message": te.errors()}
    else:
        return 'Content-Type not supported!'


@todos_blueprint.route('/todos/<user_id>/<todo_id>', methods=['PUT'])
def update_todo(user_id, todo_id):
    # Check if user is allowed to perform this operation
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json

        # TODO: Validate then update record in DB
        current_app.logger.debug("todos: %s", todo_list["todos"])
        current_app.logger.info("update to-do: %s", json)
        todo_list["todos"][int(todo_id)] = json
        return json
    else:
        return 'Content-Type not supported!'


@todos_blueprint.route('/todos/<user_id>/<todo_id>', methods=['DELETE'])
def delete_todo(user_id, todo_id):
    # Check if user is allowed to perform this operation
    # Security: rate limiting + ask for user credentials for this operation

    updated_todos = [item for item in todo_list["todos"] if item.get('id') != int(todo_id)]  # noqa: E501
    todo_list["todos"] = updated_todos

    current_app.logger.info("delete to-do: %s", todo_id)
    current_app.logger.debug("todos: %s", todo_list["todos"])

    return {"code": 200, "message": "Operation successful"}
