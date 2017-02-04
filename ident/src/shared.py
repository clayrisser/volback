import glob
import random
import yaml
import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class Shared:
    def get_platform_type(self, **kwargs):
        if kwargs['rancher_url'] or kwargs['rancher_access_key'] or kwargs['rancher_secret_key']:
            if kwargs['rancher_url'] and kwargs['rancher_access_key'] and kwargs['rancher_secret_key']:
                return 'rancher'
            else:
                exit('You are missing RANCHER_URL, RANCHER_ACCESS_KEY, or RANCHER_SECRET_KEY')
        else:
            return 'docker'

    def get_data_types(self):
        files = ''
        for file in glob.glob('/app/config/*.yml'):
            files += open(file, 'r').read()
        settings = yaml.load(files)
        return settings

    def get_mounts(self, **kwargs):
        container = kwargs['container']
        mounts = list()
        all_mounts = {}
        if kwargs['platform_type'] == 'rancher':
            all_mounts = container['data']['dockerContainer']['Mounts']
        else:
            all_mounts = container.attrs['Mounts']
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

    def get_services(self, **kwargs):
        services = list()
        if kwargs['platform_type'] == 'rancher':
            if kwargs['service']:
                service = self.__get_rancher_service(
                    data_types=kwargs['data_types'],
                    rancher_access_key=kwargs['rancher_access_key'],
                    rancher_secret_key=kwargs['rancher_secret_key'],
                    rancher_url=kwargs['rancher_url'],
                    service=kwargs['service']
                )
                return services.append(service)
            else:
                return self.__get_rancher_services(
                    blacklist=kwargs['blacklist'],
                    data_types=kwargs['data_types'],
                    rancher_access_key=kwargs['rancher_access_key'],
                    rancher_secret_key=kwargs['rancher_secret_key'],
                    rancher_url=kwargs['rancher_url']
                )
        else:
            if kwargs['service']:
                service = self.__get_docker_service(
                    data_types=kwargs['data_types'],
                    service=kwargs['service']
                )
                return services.append(service)
            else:
                return self.__get_docker_services(
                    blacklist=kwargs['blacklist'],
                    data_types=kwargs['data_types']
                )

    def rancher_call(self, call, **kwargs):
        r = requests.get(kwargs['rancher_url'] + '/v2-beta/' + call, auth=HTTPBasicAuth(kwargs['rancher_access_key'], kwargs['rancher_secret_key']), headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        return r.json()

    def __get_docker_services(self, **kwargs):
        services = list()
        for container in client.containers.list():
            data_type = 'raw'
            for key, item in kwargs['data_types'].iteritems():
                image = container.attrs['Config']['Image']
                if ':' in image:
                    image = image[:image.index(':')]
                if image == key:
                    data_type = key
            valid = False
            if kwargs['blacklist']:
                valid = True
            labels = container.attrs['Config']['Labels']
            for label in labels.iteritems():
                if kwargs['blacklist']:
                    if label[0] == 'ident' and label[1] == 'false':
                        valid = False
                else:
                    if label[0] == 'ident' and label[1] == 'true':
                        valid = True
            if valid:
                services.append({
                    'name': container.attrs['Name'][1:],
                    'container': container.attrs['Name'][1:],
                    'host': False,
                    'data_type': data_type,
                    'mounts': self.get_mounts(
                        container=container,
                        platform_type='docker'
                    )
                })
        return services

    def __get_docker_service(self, **kwargs):
        container = client.containers.get(kwargs['service'])
        data_type = 'raw'
        for key, item in kwargs['data_types'].iteritems():
            image = container.attrs['Config']['Image']
            if ':' in image:
                image = image[:image.index(':')]
            if image == key:
                data_type = key
        return {
            'name': container.attrs['Name'][1:],
            'container': container.attrs['Name'][1:],
            'host': False,
            'data_type': data_type,
            'mounts': self.get_mounts(
                container=container,
                platform_type='docker'
            )
        }

    def __get_rancher_services(self, **kwargs):
        services = list()
        for service in self.rancher_call(
            '/services',
            rancher_url=kwargs['rancher_url'],
            rancher_access_key=kwargs['rancher_access_key'],
            rancher_secret_key=kwargs['rancher_secret_key']
        )['data']:
            if service['instanceIds']:
                container = self.rancher_call(
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
                        'mounts': self.get_mounts(
                            container=container,
                            platform_type='rancher'
                        )
                    })
        return services


    def __get_rancher_service(self, **kwargs):
        for service in self.rancher_call(
            '/services',
            rancher_url=kwargs['rancher_url'],
            rancher_access_key=kwargs['rancher_access_key'],
            rancher_secret_key=kwargs['rancher_secret_key']
        )['data']:
            if service['name'] == kwargs['service']:
                if service['instanceIds']:
                    container = self.rancher_call(
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
