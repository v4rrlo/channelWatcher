from urllib import request
from channel import Channel
import threading
import config
import json
import logging
import time
import dbmanager

class ChannelWatcher:
    """
    Main class which creates threads and initiate channels
    """

    def __init__(self):
        self.channels = []
        self.threads = []

        url = 'https://api.twitch.tv/kraken/users/' + config.TWITCH_USER + '/follows/channels?limit=100'
        req = request.Request(url)
        req.add_header("Client-ID", config.API_KEY)
        resp = request.urlopen(req)
        data = json.loads(resp.read())

        logging.info('There are {} channels you are following'.format(len(data['follows'])))
        for channel_json in data['follows']:
            channel = Channel(channel_json)
            self.channels.append(channel)
        self.manager = dbmanager.DBManager()
        self.manager.create_logs_table()

    @staticmethod
    def run_jobs(jobs=[]):
        while True:
            if not jobs:
                return
            for channel in jobs:
                channel.check_status()
            time.sleep(config.REFRESH_TIME)

    def prepare_jobs(self):
        jobs = [[] for _ in range(config.NUMBER_OF_THREADS)]
        for count in range(len(self.channels)):
            jobs[count % config.NUMBER_OF_THREADS].append(self.channels[count])
        return jobs

    def create_threads(self):
        jobs = self.prepare_jobs()
        for thread_no in range(config.NUMBER_OF_THREADS):
            thread = threading.Thread(target=self.run_jobs, args=(jobs[thread_no],))
            self.threads.append(thread)
            thread.start()
