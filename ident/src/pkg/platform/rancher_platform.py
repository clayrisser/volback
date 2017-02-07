import os
import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class RancherPlatform:
    def init(self, **kwargs):
        os.popen('''
        (echo ''' + kwargs['rancher_url'] + '''; \
        echo ''' + kwargs['rancher_access_key'] + '''; \
        echo ''' + kwargs['rancher_secret_key'] + ''') | rancher config
        ''')

    def backup(self, **kwargs):
        success = False
        storage_volume = ''
        environment=kwargs['environment']
        if kwargs['storage_volume']:
            storage_volume = ' -v ' + kwargs['storage_volume'] + ':/backup'
            command = 'rancher --host ' + kwargs['service']['host'] + ' docker run --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock' + storage_volume
            for key, env in environment.iteritems():
                command += ' -e ' + key + '=' + env
            for mount in kwargs['service']['mounts']:
                command += ' -v ' + mount['source'] + ':' + mount['destination']
            command += ' jamrizzi/ident-backup:latest'
            res = os.system(command)
            if (res == 0):
                success = True
        return success

    def restore(self, **kwargs):
        success = False
        storage_volume = ''
        environment=environment
        if kwargs['storage_volume']:
            storage_volume = ' -v ' + kwargs['storage_volume'] + ':/backup'
        command = 'rancher --host ' + kwargs['service']['host'] + ' docker run --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock' + storage_volume
        for key, env in environment.iteritems():
            command += ' -e ' + key + '=' + env
        for mount in kwargs['service']['mounts']:
            command += ' -v ' + mount['source'] + ':' + mount['destination']
        command += ' jamrizzi/ident-restore:latest'
        res = os.system(command)
        if (res == 0):
            success = True
        return success

    def get_service(self, **kwargs):
        for service in self.__rancher_call(
            '/services',
            rancher_url=kwargs['rancher_url'],
            rancher_access_key=kwargs['rancher_access_key'],
            rancher_secret_key=kwargs['rancher_secret_key']
        )['data']:
            if service['name'] == kwargs['service']:
                if service['instanceIds']:
                    container = self.__rancher_call(
                        '/containers/' + random.choice(service['instanceIds']),
                        rancher_url=kwargs['rancher_url'],
                        rancher_access_key=kwargs['rancher_access_key'],
                        rancher_secret_key=kwargs['rancher_secret_key']
                    )
                    data_type = 'raw'
                    for key, item in kwargs['data_types'].iteritems():
                        image = container['data']['dockerContainer']['Image']
                        if ':' in image:
                            image = image[:image.index(':')]
                        if image == key:
                            data_type = key
                    return {
                        'name': service['name'],
                        'container': container['data']['dockerContainer']['Names'][0][1:],
                        'host': container['hostId'],
                        'data_type': data_type,
                        'mounts': self.get_mounts(
                            container=container,
                            platform_type='rancher'
                        )
                    }

    def get_services(self, **kwargs):
        services = list()
        for service in self.__rancher_call(
            '/services',
            rancher_url=kwargs['rancher_url'],
            rancher_access_key=kwargs['rancher_access_key'],
            rancher_secret_key=kwargs['rancher_secret_key']
        )['data']:
            if service['instanceIds']:
                container = self.__rancher_call(
                    '/containers/' + random.choice(service['instanceIds']),
                    rancher_url=kwargs['rancher_url'],
                    rancher_access_key=kwargs['rancher_access_key'],
                    rancher_secret_key=kwargs['rancher_secret_key']
                )
                data_type = 'raw'
                for key, item in options['data_types'].iteritems():
                    image = container['data']['dockerContainer']['Image']
                    if ':' in image:
                        image = image[:image.index(':')]
                    if image == key:
                        data_type = key
                valid = False
                if kwargs['blacklist']:
                    valid = True
                labels = container['data']['dockerContainer']['Labels']
                for label in labels.iteritems():
                    if options['blacklist']:
                        if label[0] == 'ident' and label[1] == 'false':
                            valid = False
                    else:
                        if label[0] == 'ident' and label[1] == 'true':
                            valid = True
                if valid:
                    services.append({
                        'name': service['name'],
                        'container': container['data']['dockerContainer']['Names'][0][1:],
                        'host': container['hostId'],
                        'data_type': data_type,
                        'mounts': self.__get_mounts(container)
                    })
        return services

    def __get_mounts(self, container):
        mounts = list()
        all_mounts = container['data']['dockerContainer']['Mounts']
        for mount in all_mounts:
            driver = mount['Driver'] if 'Driver' in mount else 'local'
            source = mount['Source'] if driver == 'local' else mount['Name']
            if len(source) >= 15 and source[:15] == '/var/lib/docker':
                continue
            if len(source) >= 15 and source[:15] == '/var/run/docker':
                continue
            if len(source) >= 16 and source[:16] == '/var/lib/rancher':
                continue
            if source == 'rancher-cni' or source == '/dev' or source == '/run' or source == '/lib/modules' or source == '/var/run':
                continue
            if mount['Destination'] == '/backup':
                continue
            destination = ('/volumes/' + mount['Destination'] + '/raw').replace('//', '/')
            mounts.append({
                'source': source,
                'destination': destination,
                'original_destination': mount['Destination'],
                'driver': driver,
                'mode': 'rw'
            })
        return mounts

    def __rancher_call(self, call, **kwargs):
        r = requests.get(kwargs['rancher_url'] + '/v2-beta/' + call, auth=HTTPBasicAuth(kwargs['rancher_access_key'], kwargs['rancher_secret_key']), headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        return r.json()
