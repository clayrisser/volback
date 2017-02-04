import os
import time
from helper import Helper
from shared import Shared
# from backup import Backup
# from restore import Restore

helper = Helper()
shared = Shared()
# backup = Backup()
# restore = Restore()

def main():
    options = get_options()
    platform_type = shared.get_platform_type(
        rancher_url=options['rancher_url'],
        rancher_access_key=options['rancher_access_key'],
        rancher_secret_key=options['rancher_secret_key']
    )
    services = shared.get_services(
        platform_type=platform_type,
        service=options['service'],
        rancher_access_key=options['rancher_access_key'],
        rancher_secret_key=options['rancher_secret_key'],
        rancher_url=options['rancher_url'],
        data_types=options['data_types'],
        blacklist=options['blacklist']
    )
    print(services)
    # backup.run(platform_type, services, options)

def get_options():
    options = {
        'storage_url': os.environ['STORAGE_URL'],
        'time': os.environ['TIME']
    }
    _time = 0
    if options['time'][len(options['time']) - 1:] == 'S':
        _time = int(time.time()) - int(options['time'][:len(options['time']) - 1])
    elif options['time'][len(options['time']) - 1:] == 'M':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60)
    elif options['time'][len(options['time']) - 1:] == 'H':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60)
    elif options['time'][len(options['time']) - 1:] == 'd':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24)
    elif options['time'][len(options['time']) - 1:] == 'w':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24 * 7)
    elif options['time'][len(options['time']) - 1:] == 'm':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24 * 265.25 / 12)
    elif options['time'][len(options['time']) - 1:] == 'y':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24 * 265.25)
    elif options['time'] == '':
        _time = int(time.time())
    else:
        _time = int(options['time'])
    storage_backend = False
    bucket = ''
    if options['storage_url'] != '':
        storage_backend = options['storage_url'][:options['storage_url'].index(':')]
        bucket = options['storage_url'][options['storage_url'].index(':') + 3:]
    own_container = helper.get_own_container()
    storage_volume = False
    for mount in own_container.attrs['Mounts']:
        if mount['Destination'] == '/backup':
            storage_volume = mount['Source']
    return {
        'blacklist': True if os.environ['BLACKLIST'] == 'true' else False,
        'bucket': bucket,
        'data_types': shared.get_data_types(),
        'encrypt': True if os.environ['ENCRYPT'] == 'true' else False,
        'keep_daily': os.environ['KEEP_DAILY'],
        'keep_hourly': os.environ['KEEP_HOURLY'],
        'keep_monthly': os.environ['KEEP_MONTHLY'],
        'keep_weekly': os.environ['KEEP_WEEKLY'],
        'keep_within': os.environ['KEEP_WITHIN'],
        'keep_yearly': os.environ['KEEP_YEARLY'],
        'passphrase': os.environ['PASSPHRASE'],
        'rancher_access_key': False if os.environ['RANCHER_ACCESS_KEY'] == '' else os.environ['RANCHER_ACCESS_KEY'],
        'rancher_secret_key': False if os.environ['RANCHER_SECRET_KEY'] == '' else os.environ['RANCHER_SECRET_KEY'],
        'rancher_url': False if os.environ['RANCHER_URL'] == '' else os.environ['RANCHER_URL'],
        'restore_all': True if os.environ['RESTORE_ALL'] == 'true' else False,
        'service': False if os.environ['SERVICE'] == '' else os.environ['SERVICE'],
        'storage_access_key': os.environ['STORAGE_ACCESS_KEY'],
        'storage_backend': storage_backend,
        'storage_secret_key': os.environ['STORAGE_SECRET_KEY'],
        'storage_url': os.environ['STORAGE_URL'],
        'storage_volume': storage_volume,
        'time': _time
    }

main()
