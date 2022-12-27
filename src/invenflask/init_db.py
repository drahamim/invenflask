import argparse
from importlib.resources import files
import sqlite3


def main():
    parser = argparse.ArgumentParser(
        prog="invenflask-init-db",
        description="Initialize the database for an invenflask instance"
    )
    parser.add_argument(
        '--database',
        default="database.db",
        help="Database file to (re)initialize"
    )
    args = parser.parse_args()

    schema_sql = files("invenflask").joinpath("schema.sql").read_text()
    connection = sqlite3.connect(args.database)
    try:
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()
