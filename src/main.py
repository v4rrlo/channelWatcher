__author__ = 'varrlo'

from io import BytesIO
import json
import threading
import datetime
import time
import logging
import sys
from urllib import request

# logging configuration
root = logging.getLogger()
root.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(name)-8s %(message)s', '%H:%M:%S')

file_handler = logging.FileHandler('data.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root.addHandler(file_handler)

# Bunch of constants
TWITCH_USER = 'varrlo'  # your username on twitch, needed to get list of followed users
REFRESH_TIME = 300  # after how many seconds do we check statuses again
API_KEY = 'GET YOUR OWN'
NUMBER_OF_THREADS = 10


class TwitchChannelStatus:
    """
    Main class which creates threads and initiate channels
    """

    def __init__(self):
        self.channels = []
        self.threads = []

        url = 'https://api.twitch.tv/kraken/users/' + TWITCH_USER + '/follows/channels?limit=100'
        req = request.Request(url)
        req.add_header("Client-ID", API_KEY)
        resp = request.urlopen(req)
        data = json.loads(resp.read())

        logging.info('There are {} channels you are following'.format(len(data['follows'])))
        for channel_json in data['follows']:
            channel = Channel(channel_json)
            self.channels.append(channel)

    def run_jobs(self, jobs=[]):
        while True:
            if not jobs:
                return
            for channel in jobs:
                channel.check_status()
            time.sleep(REFRESH_TIME)

    def prepare_jobs(self):
        jobs = [[] for _ in range(NUMBER_OF_THREADS)]
        for count in range(len(self.channels)):
            jobs[count % NUMBER_OF_THREADS].append(self.channels[count])
        return jobs

    def create_threads(self):
        jobs = self.prepare_jobs()
        for thread_no in range(NUMBER_OF_THREADS):
            thread = threading.Thread(target=self.run_jobs, args=(jobs[thread_no],))
            self.threads.append(thread)
            thread.start()


class Channel:
    """
    Channel class, has information about a status of a channel
    """

    # TODO: Store dates of changed status of channel - the most important part
    # example: on 24.10.15(Wed) at 4am guy went online and on 24.10.15(Wed) at 2pm went offline
    # total streamed for: 10 hours

    def __init__(self, json_data):
        self.name = json_data['channel']['name']
        self.status = 'offline'
        self.last_online = datetime.datetime.now()
        self.last_offline = datetime.datetime.now()
        self.totally_streamed = 0
        self.viewers_count = 0

    def check_status(self):
        print('Checking status of {}'.format(self.name))
        result = 'offline'
        url = 'https://api.twitch.tv/kraken/streams/' + self.name
        for attempt in range(10):
            try:
                req = request.Request(url)
                req.add_header("Client-ID", API_KEY)
                resp = request.urlopen(req)
                data = resp.read()
                break
            except request.URLError:
                logging.debug('Request for {} failed. Trying again.'.format(self.name))
                time.sleep(5)
                continue

        data_json = json.loads(data)
        if data_json['stream']:
            result = 'online'
            self.viewers_count = data_json['stream']['viewers']

        logging.info('Status of {} is {}'.format(self.name, result))

        if self.has_status_changed(result):
            self.change_status(result)
            if self.get_status() is 'online':
                self.last_online = datetime.datetime.now()
                logging.info('{} has come online'.format(self.name))
            else:
                self.last_offline = datetime.datetime.now()
                self.totally_streamed = (self.last_offline - self.last_online).total_seconds()
                logging.info('{} went offline'.format(self.name))
                logging.info('{} total streamed for {} hours'
                             .format(self.name, str(datetime.timedelta(seconds=self.totally_streamed))))

        sys.stdout.write('{}\t\t{}\t\t{}\t\t{}'.format(self.name, self.status, datetime.datetime.now(), self.viewers_count))

    def get_status(self):
        return self.status

    def has_status_changed(self, received_status):
        return received_status != self.status

    def change_status(self, target):
        self.status = target


def main():
    """
    initialising everything
    press Ctr+C to terminate application

    every REFRESH_TIME seconds threads are created, then they check channels
    and after that terminate threads

    """
    channel_watcher = TwitchChannelStatus()
    channel_watcher.create_threads()
    for thread in channel_watcher.threads:
        thread.join()
    return


if __name__ == '__main__':
    logging.info('{} Getting started'.format(datetime.datetime.now().strftime('%a %Y-%m-%d')))
    sys.stdout.write('Starting\n')
    main()
    sys.stdout.write('Goodbye\n')
