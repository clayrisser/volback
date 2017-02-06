from pkg.platform.docker_platform import DockerPlatform
from pkg.platform.rancher_platform import RancherPlatform

platform = {
    'rancher': RancherPlatform(),
    'docker': DockerPlatform()
}

class Backup:
    def run(self, **kwargs):
        if len(kwargs['services']) <= 0:
            exit('No services to backup')
        environment = {
            'PASSPHRASE': kwargs['passphrase'],
            'ENCRYPT': 'true' if kwargs['encrypt'] else 'false',
            'KEEP_WITHIN': kwargs['keep_within'],
            'HOURLY': kwargs['keep_hourly'],
            'DAILY': kwargs['keep_daily'],
            'WEEKLY': kwargs['keep_weekly'],
            'MONTHLY': kwargs['keep_monthly'],
            'YEARLY': kwargs['keep_yearly'],
            'STORAGE_ACCESS_KEY': kwargs['storage_access_key'],
            'STORAGE_SECRET_KEY': kwargs['storage_secret_key'],
            'STORAGE_URL': kwargs['storage_url']
        }
        if kwargs['platform_type'] == 'rancher':
            platform['rancher'].init(
                rancher_url=kwargs['rancher_url'],
                rancher_access_key=kwargs['rancher_access_key'],
                rancher_secret_key=kwargs['rancher_secret_key']
            )
        for service in kwargs['services']:
            has_mounts = False
            if len(service['mounts']) > 0:
                has_mounts = True
                success = False
                environment['CONTAINER_ID'] = service['container']
                environment['DATA_TYPE'] = service['data_type']
                environment['SERVICE'] = service['name']
                if kwargs['platform_type'] == 'rancher':
                    success = platform['rancher'].backup(
                        service=service,
                        storage_volume=kwargs['storage_volume'],
                        environment=environment
                    )
                else:
                    success = platform['docker'].backup(
                        service=service,
                        storage_volume=kwargs['storage_volume'],
                        environment=environment
                    )
            self.print_response(
                has_mounts=has_mounts,
                success=success,
                service=service
            )


    def print_response(self, **kwargs):
        service = kwargs['service']
        if kwargs['has_mounts']:
            data_type_pretty = '' if service['data_type'] == 'raw' else ' ~' + service['data_type']
            if (kwargs['success']):
                print('\n' + service['name'] + data_type_pretty + ': SUCCESS\n----------------------------')
            else:
                print('\n' + service['name'] + data_type_pretty + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                print(mount)
                driver_pretty = '' if mount['driver'] == 'local' else ' (' + mount['driver'] + ')'
                print('    - ' + mount['source'] + ':' + mount['original_destination'] + driver_pretty + data_type_pretty)
        else:
            print('\n' + service['name'] + ': NO VOLUMES\n-----------------------------')
