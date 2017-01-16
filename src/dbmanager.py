import sqlite3


class DBManager:
    def __init__(self):
        """
        we want to create one instance of connection per thread
        """
        self.connection = sqlite3.connect('database.db', check_same_thread=False)

    def create_logs_table(self):
        with self.connection:
            cursor = self.connection.cursor()
            table_exists = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='logs';''')
            table_exists = table_exists.fetchone()
            if table_exists is None:
                cursor.execute('''CREATE TABLE logs
                        (streamer TEXT, status INT, timestamp TEXT, viewers INT )''')
            else:
                return

    def insert_log(self, streamer_name, status, timestamp, viewers):
        with self.connection:
            cursor = self.connection.cursor()
            print("INSERT INTO logs VALUES({}, {}, {}, {})".format(streamer_name, status, timestamp, viewers))
            cursor.execute('''INSERT INTO logs VALUES(?, ?, ?, ?)''', (streamer_name, status, str(timestamp), viewers))

    def create_streamers_table(self):
        with self.connection:
            cursor = self.connection.cursor()
            table_exists = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='streamers';''')
            table_exists = table_exists.fetchone()
            if table_exists is None:
                cursor.execute('''CREATE TABLE streamers (streamer TEXT)''')
            else:
                return

    def insert_streamer(self, streamer_name):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''INSERT INTO streamers VALUES(?)''', streamer_name)
