import os
import time
from pkg.helper import Helper

class Options():

    def __init__(self):
        helper = Helper()
        self.blacklist = True if os.environ['BLACKLIST'] == 'true' else False
        self.cron_schedule = '0 ' + os.environ['CRON_SCHEDULE']
        self.debug = True if os.environ['DEBUG'] == 'true' else False
        self.encrypt = True if os.environ['ENCRYPT'] == 'true' else False
        self.host = os.environ['HOST'] if 'HOST' in os.environ else '0.0.0.0'
        self.keep_daily = os.environ['KEEP_DAILY']
        self.keep_hourly = os.environ['KEEP_HOURLY']
        self.keep_monthly = os.environ['KEEP_MONTHLY']
        self.keep_weekly = os.environ['KEEP_WEEKLY']
        self.keep_within = os.environ['KEEP_WITHIN']
        self.keep_yearly = os.environ['KEEP_YEARLY']
        self.passphrase = os.environ['PASSPHRASE']
        self.port = os.environ['PORT'] if 'PORT' in os.environ else 8888
        self.rancher_access_key = False if os.environ['RANCHER_ACCESS_KEY'] == '' else os.environ['RANCHER_ACCESS_KEY']
        self.rancher_secret_key = False if os.environ['RANCHER_SECRET_KEY'] == '' else os.environ['RANCHER_SECRET_KEY']
        self.rancher_url = False if os.environ['RANCHER_URL'] == '' else os.environ['RANCHER_URL']
        self.restore_all = True if os.environ['RESTORE_ALL'] == 'true' else False
        self.service = False if os.environ['SERVICE'] == '' else os.environ['SERVICE']
        self.storage_access_key = os.environ['STORAGE_ACCESS_KEY']
        self.storage_secret_key = os.environ['STORAGE_SECRET_KEY']
        self.storage_url = os.environ['STORAGE_URL']
        self.tag = os.environ['TAG']
        self.data_types = shared.get_data_types()
        self.own_container = helper.get_own_container()
        self.time = self.get_time(os.environ['TIME'])
        storage_backend = False
        bucket = ''
        if self.storage_url != '':
            storage_backend = self.storage_url[:self.storage_url.index(':')]
            bucket = self.storage_url[self.storage_url.index(':') + 3:]
        storage_volume = False
        for mount in own_container.attrs['Mounts']:
            if mount['Destination'] == '/backup':
                storage_volume = mount['Source']
        self.bucket = bucket
        self.storage_backend = storage_backend
        self.storage_volume = storage_volume

    def get_time(self, given_time):
        actual_time = 0
        if given_time[len(given_time) - 1:] == 'S':
            actual_time = int(time.time()) - int(given_time[:len(given_time) - 1])
        elif given_time[len(given_time) - 1:] == 'M':
            actual_time = int(time.time()) - int(int(given_time[:len(given_time) - 1]) * 60)
        elif given_time[len(given_time) - 1:] == 'H':
            actual_time = int(time.time()) - int(int(given_time[:len(given_time) - 1]) * 60 * 60)
        elif given_time[len(given_time) - 1:] == 'd':
            actual_time = int(time.time()) - int(int(given_time[:len(given_time) - 1]) * 60 * 60 * 24)
        elif given_time[len(given_time) - 1:] == 'w':
            actual_time = int(time.time()) - int(int(given_time[:len(given_time) - 1]) * 60 * 60 * 24 * 7)
        elif given_time[len(given_time) - 1:] == 'm':
            actual_time = int(time.time()) - int(int(given_time[:len(given_time) - 1]) * 60 * 60 * 24 * 265.25 / 12)
        elif given_time[len(given_time) - 1:] == 'y':
            actual_time = int(time.time()) - int(int(given_time[:len(given_time) - 1]) * 60 * 60 * 24 * 265.25)
        elif given_time == '':
            actual_time = int(time.time())
        else:
            actual_time = int(given_time)
        return actual_time
