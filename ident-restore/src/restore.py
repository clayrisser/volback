import time
import os
import yaml
import glob
import re
import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class Restore:
    def run(self, **kwargs):
        print(kwargs['data_type_details']);
        self.__borg_init(
            passphrase=kwargs['passphrase'],
            borg_repo=kwargs['borg_repo']
        )
        self.__borg_restore(
            borg_repo=kwargs['borg_repo'],
            container_id=kwargs['container_id'],
            dump_dir=kwargs['dump_dir'],
            encrypt=kwargs['encrypt'],
            mounts=kwargs['mounts'],
            passphrase=kwargs['passphrase'],
            raw_dir=kwargs['raw_dir'],
            service=kwargs['service'],
            time=kwargs['time']
        )
        if kwargs['data_type'] != 'raw':
            self.__smart_restore(
                container_id=kwargs['container_id'],
                data_type_details=kwargs['data_type_details'],
                dump_dir=kwargs['dump_dir'],
                raw_dir=kwargs['raw_dir'],
                tmp_dump_dir=kwargs['tmp_dump_dir']
            )

    def __borg_init(self, **kwargs):
        os.environ['BORG_PASSPHRASE'] = kwargs['passphrase']
        os.environ['BORG_REPO'] = kwargs['borg_repo']
        os.environ['LANG'] = 'en_US.UTF-8'

    def __borg_restore(self, **kwargs):
        no_encrypt = ''
        if (kwargs['encrypt'] == False):
            no_encrypt = '--encryption=none '
        for mount in kwargs['mounts']:
            destination = mount['Destination']
            if destination == kwargs['raw_dir']:
                destination = kwargs['dump_dir']
            name = kwargs['service'] + ':' + destination.replace('/', '#')
            name = name + '-' + self.__get_time(
                borg_repo=kwargs['borg_repo'],
                time=kwargs['time'],
                name=name
            )
            command = 'cd / && (echo y) | borg extract ::' + name
            os.system(command)

    def __smart_restore(self, **kwargs):
        os.system('ls ' + kwargs['dump_dir'])
        os.system('rm -rf ' + kwargs['tmp_dump_dir'])
        container = client.containers.get(kwargs['container_id'])
        os.system('mv ' + kwargs['dump_dir'] + ' ' + kwargs['tmp_dump_dir'])
        response = container.exec_run(kwargs['data_type_details']['restore'])
        print(response)
        os.system('rm -rf ' + kwargs['tmp_dump_dir'])

    def __get_time(self, **kwargs):
        if os.path.isdir(kwargs['borg_repo']):
            timestamp =  int(kwargs['time'])
            backups = filter(None, os.popen('borg list ' + kwargs['borg_repo']).read().split('\n'))
            exists = False
            for backup in backups:
                if (kwargs['name'] == re.findall('[\w\#\-\_\:]+(?=\-[\d]+[" "][A-Z][a-z]+)', backup)[0]):
                    _timestamp = int(re.findall('(?<=\-)[\d]+(?=[" "])', backup)[0])
                    if (_timestamp == timestamp):
                        exists = True
            if (exists == False):
                timestamp = -1
                for backup in backups:
                    if (kwargs['name'] == re.findall('[\w\#\-\_\:]+(?=\-[\d]+[" "][A-Z][a-z]+)', backup)[0]):
                        _timestamp = int(re.findall('(?<=\-)[\d]+(?=[" "])', backup)[0])
                        if (timestamp == -1):
                            timestamp = _timestamp
                        elif (_timestamp < timestamp):
                            timestamp = _timestamp
            return str(timestamp)
        else:
            return str(kwargs['time'])
