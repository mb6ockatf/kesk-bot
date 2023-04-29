from psycopg2 import connect, ProgrammingError


class DatabaseConnection:
    def __init__(self, connection_config: dict):
        self.connection = connect(**connection_config)

    def execute_query(self, query: str, data=None) -> tuple:
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
        self.connection.close()


class QueriesManager:
    def __init__(self):
        self._queries = {}

    def add_query(self, path: str, name: str):
        with open(path, "r", encoding="utf-8") as file:
            contents = file.read()
        self._queries[name] = contents

    def __getitem__(self, query_name: str) -> str:
        return self._queries[query_name]

    def __setitem__(self, query_name: str, path: str) -> str:
        return self.add_query(path, query_name)

    def items(self):
        for name, query in self._queries.items():
            yield name, query

    def __str__(self) -> str:
        result = []
        result.append("QueriesManager")
        for query_name, query in self._queries.items():
            shortened_query = query.split()[0]
            buffer = f"\t{query_name}: {shortened_query}...;"
            result.append(buffer)
        result = "\n".join(result)
        return result
