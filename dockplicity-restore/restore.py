import socket
import os

def main():
    options = get_options()
    restore(options)

def get_options():
    return {
        'allow_source_mismatch': False if 'ALLOW_SOURCE_MISMATCH' in os.environ and os.environ['ALLOW_SOURCE_MISMATCH'] == 'false' else True,
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'full_if_older_than': os.environ['FULL_IF_OLDER_THAN'] if 'FULL_IF_OLDER_THAN' in os.environ else '2W',
        'backup_dir': os.environ['BACKUP_DIR'] if 'BACKUP_DIR' in os.environ else '/volumes',
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'restore_time': os.environ['RESTORE_TIME'] if 'RESTORE_TIME' in os.environ else 'now',
        'restore_volume': os.environ['RESTORE_VOLUME'] if 'RESTORE_VOLUME' in os.environ and os.environ['RESTORE_VOLUME'] != '' else False,
        'force': True if 'FORCE' in os.environ and os.environ['FORCE'] == "true" else False
    }

def restore(options):
    restore_volume = ''
    force = ''
    backup_dir = options['backup_dir']
    if (options['restore_volume']):
        restore_volume = '--file-to-restore ' + options['restore_volume'] + ' '
        backup_dir = (options['backup_dir'] + '/' + options['restore_volume']).replace('//', '/')
    if (options['force']):
        force = '--force '
    os.system('(echo ' + options['passphrase'] + ') | duplicity restore ' + restore_volume + force + '--time ' + options['restore_time'] + ' ' + options['target_url'] + ' ' + backup_dir)

main()
