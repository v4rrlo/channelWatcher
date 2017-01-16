import sqlite3


class DBManager:
    def __init__(self):
        return

    def create_logs_table(self):
        con = sqlite3.connect('database.db')
        c = con.cursor()
        table_exists = c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='logs';''')
        table_exists = table_exists.fetchone()
        if table_exists is None:
            c.execute('''CREATE TABLE logs
                    (streamer TEXT, status INT, timestamp TEXT, viewers INT )''')
        else:
            return
