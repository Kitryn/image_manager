import sqlite3

class DbBase:
    def __init__(self, db_filename):
        self._db_filename = db_filename
        self.init_db()
    
    def init_db(self):
        with self.connect() as conn:
            with open("schema.sql") as sql_file:
                sql_as_string = sql_file.read()
            conn.executescript(sql_as_string)
    
    def connect(self):
        conn = sqlite3.connect(self._db_filename)
        # conn.set_trace_callback(print)
        return conn