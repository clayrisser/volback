import time
import os
import re
import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class Backup:

    def run(self, **kwargs):
        self.__borg_init(
            borg_repo=kwargs['borg_repo'],
            passphrase=kwargs['passphrase']
        )
        if kwargs['data_type'] != 'raw':
            self.__smart_backup(
                container_id=kwargs['container_id'],
                data_type_details=kwargs['data_type_details'],
                dump_dir=kwargs['dump_dir'],
                raw_dir=kwargs['raw_dir'],
                tmp_dump_dir=kwargs['tmp_dump_dir']
            )
        self.__borg_backup(
            borg_repo=kwargs['borg_repo'],
            encrypt=kwargs['encrypt'],
            mounts=kwargs['mounts'],
            passphrase=kwargs['passphrase'],
            service=kwargs['service']
        )

    def clean(self, **kwargs):
        prefixes = list()
        for mount in kwargs['mounts']:
            name = kwargs['service'] + mount['Destination'].replace('/', '#')
            command = '(echo y) | borg prune --prefix=' + name + ' --keep-within=' + kwargs['keep_within'] + ' --keep-hourly=' + kwargs['keep_hourly'] + ' --keep-daily=' + kwargs['keep_daily'] + ' --keep-weekly=' + kwargs['keep_weekly'] + ' --keep-monthly=' + kwargs['keep_monthly'] + ' --keep-yearly=' + kwargs['keep_yearly']
            os.system(command)

    def __borg_init(self, **kwargs):
        os.environ['BORG_PASSPHRASE'] = kwargs['passphrase']
        os.environ['BORG_REPO'] = kwargs['borg_repo']

    def __borg_backup(self, **kwargs):
        no_encrypt = ''
        if (kwargs['encrypt'] == False):
            no_encrypt = '--encryption=none '
        if os.listdir(kwargs['borg_repo']) == []:
            os.system('(echo ' + kwargs['passphrase'] + '; echo ' + kwargs['passphrase'] + '; echo) | borg init ' + no_encrypt + kwargs['borg_repo'])
        now = str(int(time.time()))
        for mount in kwargs['mounts']:
            name = kwargs['service'] + ':' + mount['Destination'].replace('/', '#') + '-' + now
            command = '(echo y) | borg create ::' + name + ' ' + mount['Destination']
            os.system(command)

    def __smart_backup(self, **kwargs):
        os.system('rm -rf ' + kwargs['tmp_dump_dir'])
        container = client.containers.get(kwargs['container_id'])
        os.system('mkdir -p ' + kwargs['tmp_dump_dir'])
        response = container.exec_run(kwargs['data_type_details']['backup'])
        print(response)
        os.system('mv ' + kwargs['tmp_dump_dir'] + ' ' + kwargs['dump_dir'] + '''
        chmod -R 700 ''' + kwargs['dump_dir'] + '''
        umount ''' + kwargs['raw_dir'] + '''
        rm -d ''' + kwargs['raw_dir'] + '''
        ''')
