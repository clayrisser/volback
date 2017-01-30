import os
from helper import Helper
from restore import Restore

helper = Helper()
restore = Restore()

def main():
    options = get_options()
    helper.mount_storage(
        borg_repo=options['borg_repo'],
        bucket=options['bucket'],
        storage_access_key=options['storage_access_key'],
        storage_backend=options['storage_backend'],
        storage_secret_key=options['storage_secret_key']
    )
    restore.run(
        borg_repo=options['borg_repo'],
        container_id=options['container_id'],
        data_type=options['data_type'],
        data_type_details=options['data_type_details'],
        dump_dir=options['dump_dir'],
        encrypt=options['encrypt'],
        mounts=options['mounts'],
        passphrase=options['passphrase'],
        raw_dir=options['raw_dir'],
        service=options['service'],
        time=options['time'],
        tmp_dump_dir=options['tmp_dump_dir']
    )

def get_options():
    options = {
        'container_id': os.environ['CONTAINER_ID'],
        'data_type': os.environ['DATA_TYPE'],
        'storage_url': os.environ['STORAGE_URL']
    }
    service = os.environ['SERVICE']
    storage_backend = False
    bucket = ''
    if options['storage_url'] != '':
        storage_backend = options['storage_url'][:options['storage_url'].index(':')]
        bucket = options['storage_url'][options['storage_url'].index(':') + 3:]
    own_container = helper.get_own_container()
    mounts = helper.get_valid_mounts(own_container)
    smart_backup_data = helper.get_smart_backup_data(
        container_id=options['container_id'],
        data_type=options['data_type']
    )
    return {
        'borg_repo': '/backup/' + service,
        'bucket': bucket,
        'container_id': options['container_id'],
        'data_type': options['data_type'],
        'data_type_details': smart_backup_data['data_type_details'],
        'dump_dir': smart_backup_data['dump_dir'],
        'dump_volume': smart_backup_data['dump_volume'],
        'encrypt': True if os.environ['ENCRYPT'] == 'true' else False,
        'mounts': mounts,
        'passphrase': os.environ['PASSPHRASE'],
        'raw_dir': smart_backup_data['raw_dir'],
        'service': service,
        'storage_access_key': os.environ['STORAGE_ACCESS_KEY'],
        'storage_backend': storage_backend,
        'storage_secret_key': os.environ['STORAGE_SECRET_KEY'],
        'storage_url': options['storage_url'],
        'time': os.environ['TIME'],
        'tmp_dump_dir': smart_backup_data['tmp_dump_dir']
    }

main()
