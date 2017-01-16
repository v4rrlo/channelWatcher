from urllib import request
import datetime
import json
import logging
import time
import config


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
                req.add_header("Client-ID", config.API_KEY)
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

        sys.stdout.write(
            '{}\t\t{}\t\t{}\t\t{}'.format(self.name, self.status, datetime.datetime.now(), self.viewers_count))

    def get_status(self):
        return self.status

    def has_status_changed(self, received_status):
        return received_status != self.status

    def change_status(self, target):
        self.status = target
