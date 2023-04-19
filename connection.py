"""
Code in this file is handling postgres database connection
"""
import os
from psycopg2 import connect, ProgrammingError


class DatabaseConnection:
    """
    handle database connection: open, close
    execute passed queries
    """
    def __init__(self, connection_config: dict):
        self.connection = connect(**connection_config)

    def execute_query(self, query: str, data=None) -> tuple:
        """
        execute SQL query with given params if some
        raise critical exception on error
        """
        result = None
        cursor = self.connection.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        try:
            result = cursor.fetchall()
        except ProgrammingError:
            result = []
        self.connection.commit()
        cursor.close()
        return result

    def close(self):
        """close database connection"""
        self.connection.close()


class QueriesManager:
    """
    preload & store SQL queries
    this object is supposed to be initialized with load_queries function (see
    below)
    """
    def __init__(self):
        self._queries = {}

    def add_query(self, path: str, name: str):
        """
        load SQL queries from files, and store them
        """
        with open(path, "r", encoding="utf-8") as file:
            contents = file.read()
        self._queries[name] = contents

    def __getitem__(self, query_name: str) -> str:
        return self._queries[query_name]

    def __setitem__(self, query_name: str, path: str) -> str:
        """more convenient way of adding queries"""
        return self.add_query(path, query_name)

    def items(self):
        """
        convenient iterator - so object looks more like a simple dictionary
        """
        for name, query in self._queries.items():
            yield name, query

    def __str__(self) -> str:
        """pretty print the object - for debugging purposes"""
        result = []
        result.append("QueriesManager")
        for query_name, query in self._queries.items():
            shortened_query = query.split()[0]
            buffer = f"\t{query_name}: {shortened_query}...;"
            result.append(buffer)
        result = "\n".join(result)
        return result

