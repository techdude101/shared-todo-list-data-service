from flask import current_app, request, Blueprint

todos_blueprint = Blueprint('todos', __name__)


@todos_blueprint.route('/todos/<user_id>', methods=['GET'])
def get_todos(user_id):
    current_app.logger.info("get to-dos for user id: %s", user_id)
    # TODO: Retrieve todos from DB for this user
    todo = {
        "data": "Stuff",
        "complete": False,
        "completed_timestamp": None
    }

    todos = [todo]
    return todos


@todos_blueprint.route('/todos/<user_id>', methods=['POST'])
def add_todo(user_id):
    current_app.info("add to-do for user id: %s", user_id)
    # Check if user is allowed to perform this operation
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        current_app.info("add to-do: %s", json)
        # TODO: Validate then add record to DB
        return json
    else:
        return 'Content-Type not supported!'


@todos_blueprint.route('/todos/<user_id>/<todo_id>', methods=['PUT'])
def update_todo(user_id, todo_id):
    # Check if user is allowed to perform this operation
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        # TODO: Validate then update record in DB
        return json
    else:
        return 'Content-Type not supported!'


@todos_blueprint.route('/todos/<user_id>/<todo_id>', methods=['DELETE'])
def delete_todo(user_id, todo_id):
    # Check if user is allowed to perform this operation
    # Security: rate limiting + ask for user credentials for this operation
    return f"Deleted {todo_id}"
