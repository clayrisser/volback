import glob
import random
import yaml
import docker
from pkg.platform.docker_platform import DockerPlatform
from pkg.platform.rancher_platform import RancherPlatform

client = docker.DockerClient(base_url='unix://var/run/docker.sock')
platform = {
    'rancher': RancherPlatform(),
    'docker': DockerPlatform()
}

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

    def get_services(self, **kwargs):
        services = list()
        if kwargs['platform_type'] == 'rancher':
            if kwargs['service']:
                service = platform['rancher'].get_service(
                    data_types=kwargs['data_types'],
                    rancher_access_key=kwargs['rancher_access_key'],
                    rancher_secret_key=kwargs['rancher_secret_key'],
                    rancher_url=kwargs['rancher_url'],
                    service=kwargs['service']
                )
                return services.append(service)
            else:
                return platform['rancher'].get_services(
                    blacklist=kwargs['blacklist'],
                    data_types=kwargs['data_types'],
                    rancher_access_key=kwargs['rancher_access_key'],
                    rancher_secret_key=kwargs['rancher_secret_key'],
                    rancher_url=kwargs['rancher_url']
                )
        else:
            if kwargs['service']:
                service = platform['docker'].get_service(
                    data_types=kwargs['data_types'],
                    service=kwargs['service']
                )
                return services.append(service)
            else:
                return platform['docker'].get_services(
                    blacklist=kwargs['blacklist'],
                    data_types=kwargs['data_types']
                )

