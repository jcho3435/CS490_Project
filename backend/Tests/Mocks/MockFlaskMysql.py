class MockFlaskMysqlConnection:

    def __init__(self):
        pass

    def cursor(self = None):
        return MockFlaskMysqlCursor()

    def commit(self = None):
        pass

    def rollback(self = None):
        pass

class MockFlaskMysqlCursor:

    def __init__(self):
        pass

    def execute(self, query, format=None):
        return None

    def fetchone(self):
        return None

    def fetchall(self):
        return None

    def close(self):
        if self:
            del self
