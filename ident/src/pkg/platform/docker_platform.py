import docker
import json

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class DockerPlatform:
    def backup(self, **kwargs):
        environment = kwargs['environment']
        response = ''
        success = False
        volumes = {}
        for env in kwargs['service']['env']:
            environment[env[:env.index('=')]] = env[env.index('=') + 1:]
        for mount in kwargs['service']['mounts']:
            volumes[mount['source']] = {
                'bind': mount['destination'],
                'mode': mount['mode']
            }
        volumes['/var/run/docker.sock'] = {
            'bind': '/var/run/docker.sock',
            'mode': 'rw'
        }
        volumes['/var/lib/docker'] = {
            'bind': '/var/lib/docker',
            'mode': 'rw'
        }
        if kwargs['storage_volume']:
            volumes[kwargs['storage_volume']] = {
                'bind': '/backup',
                'mode': 'rw'
            }
        if kwargs['debug']:
            print('>> environment: ' + json.dumps(environment))
            print('>> volumes: ' + json.dumps(volumes))
        try:
            response = client.containers.run(
                environment=environment,
                image='jamrizzi/ident-backup:latest',
                privileged=True,
                remove=True,
                volumes=volumes
            )
            success = True
        except:
            success = False
        return {
            'response': response,
            'success': success
        }

    def restore(self, **kwargs):
        environment=kwargs['environment']
        response = ''
        success = False
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
        if kwargs['debug']:
            print('>> environment: ' + environment)
            print('>> volumes: ' + volumes)
        if kwargs['storage_volume']:
            volumes[kwargs['storage_volume']] = {
                'bind': '/backup',
                'mode': 'rw'
            }
        try:
            response = client.containers.run(
                environment=environment,
                image='jamrizzi/ident-restore:latest',
                privileged=True,
                remove=True,
                volumes=volumes
            )
            success = True
        except:
            success = False
        return {
            'response': response,
            'success': success
        }

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
            'container': container.attrs['Name'][1:],
            'data_type': data_type,
            'env': self.__get_env(container, kwargs['own_container']),
            'host': False,
            'mounts': self.__get_mounts(container),
            'name': container.attrs['Name'][1:]
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
                    'container': container.attrs['Name'][1:],
                    'data_type': data_type,
                    'env': self.__get_env(container, kwargs['own_container']),
                    'host': False,
                    'mounts': self.__get_mounts(container),
                    'name': container.attrs['Name'][1:]
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

    def __get_env(self, container, own_container):
        env = list()
        for attached_env in container.attrs['Config']['Env']:
            self_override = False
            own_env = ''
            for _own_env in own_container.attrs['Config']['Env']:
                if attached_env[:attached_env.index('=')] == _own_env[:_own_env.index('=')]:
                    own_env = _own_env
                    self_override = True
            if self_override:
                env.append(own_env)
            else:
                env.append(attached_env)
        return env
