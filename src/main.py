__author__ = 'varrlo'

from io import BytesIO
import pycurl
import json
import threading
import datetime
import time
import logging
import sys

# logging configuration
root = logging.getLogger()
root.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(name)-8s %(message)s', '%H:%M:%S')

file_handler = logging.FileHandler('data.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root.addHandler(file_handler)


# Bunch of constants
TWITCH_USER = 'varrlo'      # your username on twitch, needed to get list of followed users
REFRESH_TIME = 10           # after how many seconds do we check statuses again


class TwitchChannelStatus:
    """
    Main class which creates threads and initiate channels
    """

    def __init__(self):
        self.channels = []
        self.threads = []

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://api.twitch.tv/kraken/users/' + TWITCH_USER + '/follows/channels')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        res_body = body.decode('iso-8859-1')
        j = json.loads(res_body)
        self.num_of_channels = len(j['follows'])
        logging.info('There are {} channels you are following'.format(self.num_of_channels))
        for i in range(self.num_of_channels):
            ch = Channel(j['follows'][i]['channel']['name'])
            self.channels.append(ch)

    def create_threads(self):
        for ch in self.channels:
            t = threading.Thread(target=ch.check_status, name=ch.name)
            t.start()


class Channel:
    """
    Channel class, has information about a status of a channel
    """
    # TODO: Store dates of changed status of channel - the most important part
    # example: on 24.10.15(Wed) at 4am guy went online and on 24.10.15(Wed) at 2pm went offline
    # total streamed for: 10 hours

    def __init__(self, name):
        self.name = name
        self.status = 'offline'
        self.last_online = datetime.datetime(2000, 1, 1, 23, 0, 0)
        self.last_offline = datetime.datetime(2000, 1, 2, 23, 0, 0)
        self.total_streamed = 0

    def check_status(self):

        result = 'offline'
        buffer = BytesIO()
        c = pycurl.Curl()
        for attempt in range(10):   # once in a while it needs some time to connect
            try:
                c.setopt(c.URL, 'https://api.twitch.tv/kraken/streams/' + str(self.name))
                c.setopt(c.WRITEDATA, buffer)
                c.perform()
            except pycurl.error:
                time.sleep(5)
                continue
            break

        c.close()
        body = buffer.getvalue()
        res_body = body.decode('iso-8859-1')
        j = json.loads(res_body)
        if j['stream']:
            result = 'online'
        if self.has_status_changed(result):
            self.change_status(result)
            if self.get_status() is 'online':
                self.last_online = datetime.datetime.now()
                logging.debug('{} has come online'.format(self.name))
            else:
                self.last_offline = datetime.datetime.now()
                self.total_streamed = (self.last_offline - self.last_online).total_seconds()
                logging.debug('{} went offline'.format(self.name))
                logging.debug('{} total streamed for {} hours'.format(self.name, str(datetime.timedelta(seconds=self.total_streamed))))

    def get_status(self):
        return self.status

    def has_status_changed(self, received_status):
        if received_status != self.status:
            return True
        return False

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
    count = 0
    while 1:
        sys.stdout.write('\rRun number: {}'.format(count))
        channel_watcher.create_threads()
        main_thread = threading.currentThread()  # closing threads
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
        time.sleep(REFRESH_TIME)
        count += 1
    return


if __name__ == '__main__':
    logging.info('{} Getting started'.format(datetime.datetime.now().strftime('%a %Y-%m-%d')))
    sys.stdout.write('Starting\n')
    main()
    sys.stdout.write('Goodbye\n')
