import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class DockerPlatform:
    def backup(self, **kwargs):
        success = False
        environment = kwargs['environment']
        volumes = {}
        for mount in kwargs['service']['mounts']:
            volumes[mount['source']] = {
                'bind': mount['destination'],
                'mode': mount['mode']
            }
            volumes['/var/run/docker.sock'] = {
                'bind': '/var/run/docker.sock',
                'mode': 'rw'
            }
            if kwargs['storage_volume']:
                volumes[kwargs['storage_volume']] = {
                    'bind': '/backup',
                    'mode': 'rw'
                }
            try:
                response = client.containers.run(
                    image='jamrizzi/ident-backup:latest',
                    volumes=volumes,
                    remove=True,
                    privileged=True,
                    environment=environment
                )
                success = True
            except:
                success = False
        return success

    def get_service(self, **kwargs):
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
            'mounts': self.__get_mounts(
                container=container,
                platform_type='docker'
            )
        }

    def get_services(self, **kwargs):
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
                    'mounts': self.__get_mounts(container)
                })
        return services

    def __get_mounts(self, container):
        mounts = list()
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
