import os
import re
import time
from pkg.platform.docker_platform import DockerPlatform
from pkg.platform.rancher_platform import RancherPlatform

platform = {
    'docker': DockerPlatform(),
    'rancher': RancherPlatform()
}

class Restore:
    def run(self, **kwargs):
        if kwargs['services'] == None or len(kwargs['services']) <= 0:
            exit('No services to restore')
        if os.popen('ls /backup').read() == '':
            exit('Storage repository is empty')
        environment = {
            'ENCRYPT': kwargs['encrypt'],
            'PASSPHRASE': kwargs['passphrase'],
            'STORAGE_ACCESS_KEY': kwargs['storage_access_key'],
            'STORAGE_SECRET_KEY': kwargs['storage_secret_key'],
            'STORAGE_URL': kwargs['storage_url']
        }
        if kwargs['platform_type'] == 'rancher':
            platform['rancher'].init(
                rancher_access_key=kwargs['rancher_access_key'],
                rancher_secret_key=kwargs['rancher_secret_key'],
                rancher_url=kwargs['rancher_url']
            )
        for service in kwargs['services']:
            has_mounts = False
            response = ''
            success = False
            if len(service['mounts']) > 0:
                has_mounts = True
                timestamp = self.__get_time(
                    passphrase=kwargs['passphrase'],
                    service=service,
                    time=kwargs['time']
                )
                environment['CONTAINER_ID'] = service['container']
                environment['DATA_TYPE'] = service['data_type']
                environment['SERVICE'] = service['name']
                environment['TIME'] = timestamp
                if kwargs['platform_type'] == 'rancher':
                    package = platform['rancher'].restore(
                        environment=environment,
                        service=service,
                        storage_volume=kwargs['storage_volume']
                    )
                    response = package['response']
                    success = package['success']
                else:
                    package = platform['docker'].restore(
                        environment=environment,
                        service=service,
                        storage_volume=kwargs['storage_volume']
                    )
                    response = package['response']
                    success = package['success']
            self.__print_response(
                debug=kwargs['debug'],
                has_mounts=has_mounts,
                response=response,
                service=service,
                success=success,
                timestamp=timestamp
            )

    def __print_response(self, **kwargs):
        service = kwargs['service']
        if kwargs['has_mounts']:
            data_type_pretty = '' if service['data_type'] == 'raw' else ' ~' + service['data_type']
            if (kwargs['success']):
                print('\n' + service['name'] + data_type_pretty + ' (' + time.strftime("%B %d, %Y %I:%M %p %Z", time.localtime(int(kwargs['timestamp']))) + '): SUCCESS\n----------------------------')
            else:
                print('\n' + service['name'] + data_type_pretty + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                driver_pretty = '' if mount['driver'] == 'local' else ' (' + mount['driver'] + ')'
                print('    - ' + mount['source'] + ':' + mount['original_destination'] + driver_pretty + data_type_pretty)
        else:
            print('\n' + service['name'] + ': NO VOLUMES\n-----------------------------')

    def __get_time(self, **kwargs):
        service = kwargs['service']
        os.environ['BORG_PASSPHRASE'] = kwargs['passphrase']
        borg_repo = '/backup/' + service['name']
        if os.path.isdir(borg_repo):
            timestamp = -1
            backups = filter(None, os.popen('borg list ' + borg_repo).read().split('\n'))
            for backup in backups:
                _timestamp = int(re.findall('(?<=\-)[\d]+(?=[" "])', backup)[0])
                if (_timestamp <= kwargs['time']):
                    if (_timestamp > timestamp):
                        timestamp = _timestamp
                elif (timestamp == -1 or _timestamp < timestamp):
                    timestamp = _timestamp
            return str(timestamp)
        else:
            return str(kwargs['time'])
        if kwargs['debug']:
            print('--------- jamrizzi/ident-restore')
            print(kwargs['response'])
