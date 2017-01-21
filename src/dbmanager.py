import sqlite3


class DBManager:
    def __init__(self, path='database.db'):
        """
        we want to create one instance of connection per thread
        """
        self.connection = sqlite3.connect(path, check_same_thread=False)

    def create_logs_table(self):
        with self.connection:
            cursor = self.connection.cursor()
            table_exists = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='logs';''')
            table_exists = table_exists.fetchone()
            if table_exists is None:
                cursor.execute('''CREATE TABLE logs (streamer TEXT, status INT, timestamp DATETIME, viewers INT )''')
            else:
                return

    def insert_log(self, streamer_name, status, timestamp, viewers):
        with self.connection:
            cursor = self.connection.cursor()
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
            streamer_exists = cursor.execute('''SELECT * FROM streamers WHERE streamers.streamer = ?''', (streamer_name,))
            streamer_exists = streamer_exists.fetchone()
            if streamer_exists is None:
                cursor.execute('''INSERT INTO streamers VALUES(?)''', (streamer_name,))
            else:
                return

    def get_streamers(self):
        streamers = []
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''SELECT * FROM streamers;''')

            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                streamers.append(row[0])
        return streamers

    def get_streamer_data(self, name):
        data = []
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''SELECT * FROM logs WHERE logs.streamer = ? ORDER BY logs.timestamp DESC;''', (name,))

            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                data.append((row[2], row[3]))
        return data

    def get_streamer_data_specific_date(self, name, date, end_date=None):
        if end_date is None or end_date == '':
            end_date = date
            end_date = end_date[:-1] + str(int(date[-1]) + 1)
        data = []
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                '''SELECT * FROM logs WHERE logs.streamer = ? AND logs.status = 1 AND logs.timestamp BETWEEN ? AND ?;''',
                (name, date, end_date))

            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                data.append((row[2], row[3]))
        return data
