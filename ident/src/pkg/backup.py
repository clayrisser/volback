from pkg.platform.docker_platform import DockerPlatform
from pkg.platform.rancher_platform import RancherPlatform

platform = {
    'docker': DockerPlatform(),
    'rancher': RancherPlatform()
}

class Backup:
    def run(self, **kwargs):
        if kwargs['services'] == None or len(kwargs['services']) <= 0:
            exit('No services to backup')
        environment = {
            'DAILY': kwargs['keep_daily'],
            'ENCRYPT': 'true' if kwargs['encrypt'] else 'false',
            'HOURLY': kwargs['keep_hourly'],
            'KEEP_WITHIN': kwargs['keep_within'],
            'MONTHLY': kwargs['keep_monthly'],
            'PASSPHRASE': kwargs['passphrase'],
            'STORAGE_ACCESS_KEY': kwargs['storage_access_key'],
            'STORAGE_SECRET_KEY': kwargs['storage_secret_key'],
            'STORAGE_URL': kwargs['storage_url'],
            'WEEKLY': kwargs['keep_weekly'],
            'YEARLY': kwargs['keep_yearly']
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
                environment['CONTAINER_ID'] = service['container']
                environment['DATA_TYPE'] = service['data_type']
                environment['SERVICE'] = service['name']
                if kwargs['platform_type'] == 'rancher':
                    package = platform['rancher'].backup(
                        debug=kwargs['debug'],
                        environment=environment,
                        service=service,
                        storage_volume=kwargs['storage_volume']
                    )
                    response = package['response']
                    success = package['success']
                else:
                    package = platform['docker'].backup(
                        debug=kwargs['debug'],
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
                success=success
            )

    def __print_response(self, **kwargs):
        service = kwargs['service']
        if kwargs['has_mounts']:
            data_type_pretty = '' if service['data_type'] == 'raw' else ' ~' + service['data_type']
            if (kwargs['success']):
                print(service['name'] + data_type_pretty + ': SUCCESS\n----------------------------')
            else:
                print(service['name'] + data_type_pretty + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                driver_pretty = '' if mount['driver'] == 'local' else ' (' + mount['driver'] + ')'
                print('    - ' + mount['source'] + ':' + mount['original_destination'] + driver_pretty + data_type_pretty)
        else:
            print('\n' + service['name'] + ': NO VOLUMES\n-----------------------------')
        if kwargs['debug']:
            print('<<<<<<<<<<<< jamrizzi/ident-backup >>>>>>>>>>>>')
            print(kwargs['response'])
            print('<<<<<<<<<<<<')
        print('')
