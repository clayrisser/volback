import socket
import os

def main():
    options = get_options()
    backup(options)
    clean(options)

def get_options():
    return {
        'allow_source_mismatch': eval((os.environ['ALLOW_SOURCE_MISMATCH'] if 'ALLOW_SOURCE_MISMATCH' in os.environ else 'true').title()),
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'backup_type': os.environ['BACKUP_TYPE'] if 'BACKUP_TYPE' in os.environ else 'incr',
        'full_if_older_than': os.environ['FULL_IF_OLDER_THAN'] if 'FULL_IF_OLDER_THAN' in os.environ else '2W',
        'backup_dir': os.environ['BACKUP_DIR'] if 'BACKUP_DIR' in os.environ else '/volumes',
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'remove_older_than': os.environ['REMOVE_OLDER_THAN'] if 'REMOVE_OLDER_THAN' in os.environ else '6M',
        'remove_all_but_n_full': os.environ['REMOVE_ALL_BUT_N_FULL'] if 'REMOVE_ALL_BUT_N_FULL' in os.environ else '12',
        'remove_all_inc_but_of_n_full': os.environ['REMOVE_ALL_INC_BUT_OF_N_FULL'] if 'REMOVE_ALL_INC_BUT_OF_N_FULL' in os.environ else '144'
    }

def backup(options):
    allow_source_mismatch = ''
    if (options['allow_source_mismatch']):
        allow_source_mismatch = '--allow-source-mismatch '
    os.system('echo ' + options['passphrase'] + '; echo ' + options['passphrase'] + ') | duplicity ' + options['backup_type'] + ' ' + allow_source_mismatch + '--full-if-older-than ' + options['full_if_older_than'] + ' ' + options['backup_dir'] + ' ' + options['target_url'])
    clean();

def clean(options):
    os.system('''
    duplicity remove-older-than ''' + options['remove_older_than'] + ' --force "' + options['target_url'] + '''"
    duplicity remove-all-but-n-full ''' + options['remove_all_but_n_full'] + ' --force "' + options['target_url'] + '''"
    duplicity remove-all-inc-of-but-n-full ''' + options['remove_all_inc_but_of_n_full'] + ' --force "' + options['target_url'] + '''"
    duplicity cleanup --extra-clean --force "''' + options['target_url'] + '''"
    ''')

main()
