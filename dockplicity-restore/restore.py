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
    data_type = get_data_type(options)
    restore(options, data_type)

def get_options():
    options = {
        'restore_dir': os.environ['RESTORE_DIR'] if 'RESTORE_DIR' in os.environ else '/volumes',
        'data_type': os.environ['DATA_TYPE'] if 'DATA_TYPE' in os.environ else 'raw'
    }
    raw_dir = ''
    tmp_dump_dir = ''
    me = get_me()
    for mount in me.attrs['Mounts']:
        if len(mount['Destination']) > len(options['restore_dir']) and mount['Destination'][:len(options['restore_dir']) + 1] == options['restore_dir'] + '/':
            raw_dir = mount['Destination']
            tmp_dump_dir = (raw_dir + '/dockplicity_backup').replace('//', '/')
    volume_dir = raw_dir[:len(raw_dir) - 4]
    dump_dir = (volume_dir + '/' + options['data_type']).replace('//', '/')
    return {
        'allow_source_mismatch': False if 'ALLOW_SOURCE_MISMATCH' in os.environ and os.environ['ALLOW_SOURCE_MISMATCH'] == 'false' else True,
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'restore_dir': options['restore_dir'],
        'raw_dir': raw_dir,
        'tmp_dump_dir': tmp_dump_dir,
        'dump_dir': dump_dir,
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'data_type': options['data_type'],
        'volume_dir': volume_dir,
        'restore_time': os.environ['RESTORE_TIME'] if 'RESTORE_TIME' in os.environ else 'now',
        'restore_volume': os.environ['RESTORE_VOLUME'] if 'RESTORE_VOLUME' in os.environ and os.environ['RESTORE_VOLUME'] != '' else False,
        'force': True if 'FORCE' in os.environ and os.environ['FORCE'] == "true" else False,
        'container_id': os.environ['CONTAINER_ID'] if 'CONTAINER_ID' in os.environ else ''
    }

def get_data_type(options):
    if options['data_type'] != 'raw':
        files = ""
        for file in glob.glob("/scripts/config/*.yml"):
            files += open(file, 'r').read()
        settings = yaml.load(files)
        setting = settings[options['data_type']]
        envs = re.findall('(?<=\<)[A-Z\d\-\_]+(?=\>)', setting['restore'])
        for env in envs:
            setting['restore'] = setting['restore'].replace('<' + env + '>', os.environ[env] if env in os.environ else '')
        setting['restore'] = ('/bin/sh -c "' + setting['restore'] + '"').replace('%DUMP%', setting['data-location'] + '/dockplicity_backup/' + setting['backup-file']).replace('//', '/')
        return setting
    else:
        return 'raw'

def restore(options, data_type):
    restore_volume = ''
    force = ''
    restore_dir = options['restore_dir']
    if (options['restore_volume']):
        file_to_restore = options['restore_volume']
        if file_to_restore[0] == '/':
            file_to_restore = file_to_restore[1:]
        restore_volume = '--file-to-restore ' + file_to_restore + ' '
        restore_dir = (options['restore_dir'] + '/' + options['restore_volume']).replace('//', '/')
    if (options['force']):
        force = '--force '
    os.system('(echo ' + options['passphrase'] + ') | duplicity restore ' + restore_volume + force + '--time ' + options['restore_time'] + ' ' + options['target_url'] + ' ' + restore_dir)
    if data_type != 'raw':
        os.system('rm -rf ' + options['tmp_dump_dir'])
        container = client.containers.get(options['container_id'])
        os.system('mv ' + options['dump_dir'] + ' ' + options['tmp_dump_dir'])
        response = container.exec_run(data_type['restore'])
        print(response)
        os.system('rm -rf ' + options['tmp_dump_dir'])

def get_me():
    ip = socket.gethostbyname(socket.gethostname())
    for container in client.containers.list():
        if (container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress'] == ip):
            return container

main()
