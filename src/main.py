import sys
from channel import *
from channelwatcher import ChannelWatcher

# logging configuration
root = logging.getLogger()
root.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(levelname)-8s %(name)-8s %(message)s', '%H:%M:%S')

file_handler = logging.FileHandler('data.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root.addHandler(file_handler)


def main():
    """
    initialising everything
    press Ctr+C to terminate application

    every REFRESH_TIME seconds threads are created, then they check channels
    and after that terminate threads

    """
    channel_watcher = ChannelWatcher()
    channel_watcher.create_threads()
    for thread in channel_watcher.threads:
        thread.join()
    return


if __name__ == '__main__':
    logging.info('{} Getting started'.format(datetime.datetime.now().strftime('%a %Y-%m-%d')))
    sys.stdout.write('Starting\n')
    main()
    sys.stdout.write('Goodbye\n')
