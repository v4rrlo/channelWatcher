# channelWatcher
Application which monitors Twitch channels user has followed

Right now everything is stored in src/data.log
Application must run all the time to store data

Create config.py file with variables:
* API_KEY = ''            - get your own key
* TWITCH_USER = 'varrlo'  - your username on twitch, needed to get list of followed users
* REFRESH_TIME = 300      - after how many seconds do we check statuses again
* NUMBER_OF_THREADS = 10  - number of threads running tasks