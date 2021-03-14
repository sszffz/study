import mysql.connector
from mysql.connector.connection_cext import CMySQLConnection


def is_database_exist(db_conn: CMySQLConnection, database_name: str) -> bool:
    """
    test whether a specified database exists or not
    :param db_conn:
        database connection to mysql server
    :param database_name:
        database name
    :return:
    """
    if not db_conn:
        return False

    cursor = db_conn.cursor()
    sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(database_name)
    cursor.execute(sql)
    return True if cursor.fetchall() else False


# def is_database_exist(db_conn: CMySQLConnection, database_name: str) -> bool:
#     """
#     test whether a specified database exists or not
#     :param db_conn:
#     :param database_name:
#     :return:
#     """
#     if not db_conn:
#         return False
#
#     cmd = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(database_name)
#     db_cursor = db_conn.cursor()
#     db_cursor.execute(cmd)
#
#     result = True if db_cursor.fetchone() else False
#     db_cursor.close()
#
#     return result


def is_table_exist(db_conn: CMySQLConnection, database_name: str, table_name: str) -> bool:
    """
    Test whether a table exists in a specified database
    :param db_conn:
    :param database_name:
    :param table_name:
    :return:
    """
    if not db_conn:
        return False

    cmd = "SELECT * FROM information_schema.tables WHERE table_schema = '{}' " \
          "AND table_name = '{}'".format(database_name, table_name)
    db_cursor = db_conn.cursor()
    db_cursor.execute(cmd)

    result = True if db_cursor.fetchone() else False
    db_cursor.close()

    return result

# if __name__ == "__main__":
#     db_conn = mysql.connector.connect(user="root", password = "XiaoYouZi2007", host="localhost")
#     print(is_database_exist(db_conn, "mysql"))
#     pass