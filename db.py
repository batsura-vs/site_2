import sqlite3


class OpenDb:
    def __init__(self, table_name):
        self.con = sqlite3.connect(table_name)

    def __enter__(self):
        self.cur = self.con.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.commit()
        self.con.commit()
