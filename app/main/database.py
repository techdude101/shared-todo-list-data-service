import mysql.connector
from mysql.connector.errors import DatabaseError

import os

# TODO: DB connection pooling - https://dev.mysql.com/doc/connector-python/en/connector-python-connection-pooling.html  # noqa: E501


def get_database_connection():
    """Get a new connection to a database.

    Returns:
        mysql.connector.MySQLConnection: MySQL database connection
    """

    host = os.getenv("MYSQLDB_HOST")
    user = os.getenv("MYSQLDB_USER")
    password = os.getenv("MYSQLDB_PASSWORD")
    db = os.getenv("MYSQLDB_DB")

    if (host and user and password and db):
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db,
        )
    else:
        return mysql.connector.connect(
            host="localhost",
            user="todo_user",
            password="<password goes here>",
            database="<db name>"
        )


def call_stored_procedure(db_connection: mysql.connector.MySQLConnection,
                          procedure_name: str,
                          args: tuple):
    """Call a stored procedure.

    Args:
        db_connection (mysql.connector.MySQLConnection):
        MySQL database connection
        procedure_name (str): the name of the stored procedure
        args (tuple): stored procedure arguments

    Raises:
        DatabaseError: the database error

    Returns:
        None: no return value
    """
    db_cursor = None

    try:
        db_cursor = db_connection.cursor()
        result = db_cursor.callproc(procedure_name, args)
        db_connection.commit()

        return result
    except DatabaseError as db_error:
        raise DatabaseError(db_error)
    finally:
        if db_cursor:
            db_cursor.close()
        if db_connection:
            db_connection.close()


def check_todo_exists(db_connection: mysql.connector.MySQLConnection,
                      user_id: int, todo_id: int) -> bool:
    query = """SELECT todo_id FROM db_todo.tbl_todo WHERE user_id = (%s) AND todo_id = (%s) LIMIT 1"""  # noqa: E501

    db_cursor = db_connection.cursor()
    db_cursor.execute(query, (user_id, todo_id))
    records = db_cursor.fetchall()

    if len(records) == 0:
        return False
    return True
