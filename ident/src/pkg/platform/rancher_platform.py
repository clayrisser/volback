import docker
import os
import random
import requests
import uuid
from requests.auth import HTTPBasicAuth

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class RancherPlatform:
    def init(self, **kwargs):
        os.popen('''
        (echo ''' + kwargs['rancher_url'] + '''; \
        echo ''' + kwargs['rancher_access_key'] + '''; \
        echo ''' + kwargs['rancher_secret_key'] + ''') | rancher config
        ''')

    def backup(self, **kwargs):
        environment=kwargs['environment']
        name=uuid.uuid4().hex
        response = ''
        storage_volume = ''
        success = False
        if kwargs['storage_volume']:
            storage_volume = ' -v ' + kwargs['storage_volume'] + ':/backup'
        command = 'rancher --host ' + kwargs['service']['host'] + ' docker run --name ' + name + ' --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker' + storage_volume
        for key, env in environment.iteritems():
            command += ' -e ' + key + '=' + env
        for env in kwargs['service']['env']:
            command += ' -e ' + env
        for mount in kwargs['service']['mounts']:
            command += ' -v ' + mount['source'] + ':' + mount['destination']
        command += ' jamrizzi/ident-backup:latest'
        if kwargs['debug']:
            print('>> ' + command)
        try:
            os.popen(command)
            response = os.popen('rancher --host ' + kwargs['service']['host'] + ' docker logs ' + name).read()
            os.popen('rancher --host ' + kwargs['service']['host'] + ' docker rm ' + name)
            success = True
        except:
            success = False
        return {
            'response': response,
            'success': success
        }

    def restore(self, **kwargs):
        environment=kwargs['environment']
        name=uuid.uuid4().hex
        response = ''
        storage_volume = ''
        success = False
        if kwargs['storage_volume']:
            storage_volume = ' -v ' + kwargs['storage_volume'] + ':/backup'
        command = 'rancher --host ' + kwargs['service']['host'] + ' docker run --name ' + name + ' --privileged -v /var/run/docker.sock:/var/run/docker.sock' + storage_volume
        for key, env in environment.iteritems():
            command += ' -e ' + key + '=' + env
        for env in kwargs['service']['env']:
            command += ' -e ' + env
        for mount in kwargs['service']['mounts']:
            command += ' -v ' + mount['source'] + ':' + mount['destination']
        command += ' jamrizzi/ident-restore:latest'
        if kwargs['debug']:
            print('>> ' + command)
        try:
            os.popen(command)
            response = os.popen('rancher --host ' + kwargs['service']['host'] + ' docker logs ' + name).read()
            os.popen('rancher --host ' + kwargs['service']['host'] + ' docker rm ' + name)
            success = True
        except:
            success = False
        return {
            'response': response,
            'success': success
        }

    def get_service(self, **kwargs):
        for service in self.__rancher_call(
            '/services',
            rancher_access_key=kwargs['rancher_access_key'],
            rancher_secret_key=kwargs['rancher_secret_key'],
            rancher_url=kwargs['rancher_url']
        )['data']:
            if service['name'] == kwargs['service']:
                if service['instanceIds']:
                    container = self.__rancher_call(
                        '/containers/' + random.choice(service['instanceIds']),
                        rancher_access_key=kwargs['rancher_access_key'],
                        rancher_secret_key=kwargs['rancher_secret_key'],
                        rancher_url=kwargs['rancher_url']
                    )
                    data_type = 'raw'
                    for key, item in kwargs['data_types'].iteritems():
                        image = container['data']['dockerContainer']['Image']
                        if ':' in image:
                            image = image[:image.index(':')]
                        if image == key:
                            data_type = key
                    return {
                        'container': container['data']['dockerContainer']['Names'][0][1:],
                        'data_type': data_type,
                        'env': self.__get_env(service, kwargs['own_container']),
                        'host': container['hostId'],
                        'mounts': self.__get_mounts(container),
                        'name': service['name']
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
                    rancher_access_key=kwargs['rancher_access_key'],
                    rancher_secret_key=kwargs['rancher_secret_key'],
                    rancher_url=kwargs['rancher_url']
                )
                data_type = 'raw'
                for key, item in kwargs['data_types'].iteritems():
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
                    if kwargs['blacklist']:
                        if label[0] == 'ident' and label[1] == 'false':
                            valid = False
                    else:
                        if label[0] == 'ident' and label[1] == 'true':
                            valid = True
                if valid:
                    services.append({
                        'container': container['data']['dockerContainer']['Names'][0][1:],
                        'data_type': data_type,
                        'env': self.__get_env(service, kwargs['own_container']),
                        'host': container['hostId'],
                        'mounts': self.__get_mounts(container),
                        'name': service['name']
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

    def __get_env(self, service, own_container):
        launchConfig = service['data']['fields']['launchConfig']
        environment = None
        env = list()
        if 'environment' in launchConfig:
            environment = launchConfig['environment']
            for attached_key, attached_env in environment.iteritems():
                self_override = False
                own_env = ''
                for own_key, _own_env in environment.iteritems():
                    if attached_key == own_key:
                        own_env = own_key + '=' + _own_env
                        self_override = True
                if self_override:
                    env.append(own_env)
                else:
                    env.append(attached_env)
        return env

    def __rancher_call(self, call, **kwargs):
        r = requests.get(kwargs['rancher_url'] + '/v2-beta/' + call, auth=HTTPBasicAuth(kwargs['rancher_access_key'], kwargs['rancher_secret_key']), headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        return r.json()
