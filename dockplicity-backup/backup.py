import socket
import time
import os
import yaml
import glob
import re
import docker
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def main():
    options = get_options()
    backup(options)
    clean(options)

def get_options():
    options = {
        'backup_dir': os.environ['BACKUP_DIR'] if 'BACKUP_DIR' in os.environ else '/volumes',
        'data_type': os.environ['DATA_TYPE'] if 'DATA_TYPE' in os.environ else 'raw'
    }
    data_type_details = ''
    raw_dir = ''
    tmp_dump_dir = ''
    dump_volume = ''
    dump_dir = ''
    if options['data_type'] != 'raw':
        data_type_details = get_data_type_details(options['data_type'])
        own_container = get_own_container()
        for mount in own_container.attrs['Mounts']:
            if mount['Destination'] == (options['backup_dir'] + '/' + data_type_details['data-location'] + '/raw').replace('//', '/'):
                raw_dir = mount['Destination']
                tmp_dump_dir = (raw_dir + '/dockplicity_backup').replace('//', '/')
                dump_volume = raw_dir[:len(raw_dir) - 4]
                dump_dir = (dump_volume + '/' + options['data_type']).replace('//', '/')
    return {
        'allow_source_mismatch': False if 'ALLOW_SOURCE_MISMATCH' in os.environ and os.environ['ALLOW_SOURCE_MISMATCH'] == 'false' else True,
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'backup_type': os.environ['BACKUP_TYPE'] if 'BACKUP_TYPE' in os.environ else 'incr',
        'full_if_older_than': os.environ['FULL_IF_OLDER_THAN'] if 'FULL_IF_OLDER_THAN' in os.environ else '2W',
        'backup_dir': options['backup_dir'],
        'raw_dir': raw_dir,
        'tmp_dump_dir': tmp_dump_dir,
        'dump_dir': dump_dir,
        'encrypt': True if os.environ['ENCRYPT'] == 'true' else False,
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'remove_older_than': os.environ['REMOVE_OLDER_THAN'] if 'REMOVE_OLDER_THAN' in os.environ else '6M',
        'remove_all_but_n_full': os.environ['REMOVE_ALL_BUT_N_FULL'] if 'REMOVE_ALL_BUT_N_FULL' in os.environ else '12',
        'remove_all_inc_but_of_n_full': os.environ['REMOVE_ALL_INC_BUT_OF_N_FULL'] if 'REMOVE_ALL_INC_BUT_OF_N_FULL' in os.environ else '144',
        'data_type': options['data_type'],
        'dump_volume': dump_volume,
        'data_type_details': data_type_details,
        'container_id': os.environ['CONTAINER_ID'] if 'CONTAINER_ID' in os.environ else ''
    }

def get_data_type_details(data_type):
    if data_type != 'raw':
        files = ""
        for file in glob.glob("/scripts/config/*.yml"):
            files += open(file, 'r').read()
        settings = yaml.load(files)
        setting = settings[data_type]
        envs = re.findall('(?<=\<)[A-Z\d\-\_]+(?=\>)', setting['restore'])
        for env in envs:
            setting['backup'] = setting['backup'].replace('<' + env + '>', os.environ[env] if env in os.environ else '')
        setting['backup'] = ('/bin/sh -c "' + setting['backup'] + '"').replace('%DUMP%', setting['data-location'] + '/dockplicity_backup/' + setting['backup-file']).replace('//', '/')
        return setting
    else:
        return 'raw'

def backup(options):
    if options['data_type'] != 'raw':
        os.system('rm -rf ' + options['tmp_dump_dir'])
        container = client.containers.get(options['container_id'])
        os.system('mkdir -p ' + options['tmp_dump_dir'])
        response = container.exec_run(options['data_type_details']['backup'])
        print(response)
        os.system('mv ' + options['tmp_dump_dir'] + ' ' + options['dump_dir'] + '''
        chmod -R 700 ''' + options['dump_dir'] + '''
        umount ''' + options['raw_dir'] + '''
        rm -d ''' + options['raw_dir'] + '''
        ''')
    allow_source_mismatch = ''
    if (options['encrypt'] == False):
        no_encrypt = '--no-encrypt '
    if (options['allow_source_mismatch']):
        allow_source_mismatch = '--allow-source-mismatch '
    os.system('(echo ' + options['passphrase'] + '; echo ' + options['passphrase'] + ') | duplicity ' + options['backup_type'] + ' ' + allow_source_mismatch + no_encrypt + '--full-if-older-than ' + options['full_if_older_than'] + ' ' + options['backup_dir'] + ' ' + options['target_url'])

def clean(options):
    os.system('''
    duplicity remove-older-than ''' + options['remove_older_than'] + ' --force "' + options['target_url'] + '''"
    duplicity remove-all-but-n-full ''' + options['remove_all_but_n_full'] + ' --force "' + options['target_url'] + '''"
    duplicity remove-all-inc-of-but-n-full ''' + options['remove_all_inc_but_of_n_full'] + ' --force "' + options['target_url'] + '''"
    duplicity cleanup --extra-clean --force "''' + options['target_url'] + '''"
    ''')

def get_own_container():
    ip = socket.gethostbyname(socket.gethostname())
    for container in client.containers.list():
        if (container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress'] == ip):
            return container

main()
