import docker
import glob
import yaml
import socket
import os
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def main():
    options = get_options()
    platform_type = get_platform_type(options)
    services = get_services(platform_type, options)
    backup_services(platform_type, services, options)

def get_options():
    return {
        'rancher_url': os.environ['RANCHER_URL'] if 'RANCHER_URL' in os.environ else False,
        'rancher_access_key': os.environ['RANCHER_ACCESS_KEY'] if 'RANCHER_ACCESS_KEY' in os.environ else False,
        'rancher_secret_key': os.environ['RANCHER_SECRET_KEY'] if 'RANCHER_SECRET_KEY' in os.environ else False,
        'volume_driver': os.environ['VOLUME_DRIVER'] if 'VOLUME_DRIVER' in os.environ else 'local',
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'blacklist': False if os.environ['BLACKLIST'] != 'true' else True,
        'service': False if os.environ['SERVICE'] == '' else os.environ['SERVICE'],
        'restore_all': True if os.environ['RESTORE_ALL'] == 'true' else False,
        'data_types': get_data_types(),
        'remove_all_inc_but_of_n_full': os.environ['REMOVE_ALL_INC_BUT_OF_N_FULL'] if 'REMOVE_ALL_INC_BUT_OF_N_FULL' in os.environ else '144'
    }

def get_platform_type(options):
    if options['rancher_url']:
        return 'rancher'
    else:
        return 'docker'

def get_services(platform_type, options):
    services = list()
    if platform_type == 'rancher':
        services = list()
    else:
        if options['service']:
            container = client.containers.get(options['service'])
            data_type = 'raw'
            for key, item in options['data_types'].iteritems():
                image = container.attrs['Config']['Image']
                if ':' in image:
                    image = image[:image.index(':')]
                if image == key:
                    data_type = key
            services.append({
                'name': container.attrs['Name'],
                'host': False,
                'data_type': data_type,
                'volumes': get_volumes(platform_type, options, container)
            })
        elif options['restore_all']:
            for container in client.containers.list():
                data_type = 'raw'
                for key, item in options['data_types'].iteritems():
                    image = container.attrs['Config']['Image']
                    if ':' in image:
                        image = image[:image.index(':')]
                    if image == key:
                        data_type = key
                    valid = False
                    if options['blacklist']:
                        valid = True
                    labels = container.attrs['Config']['Labels']
                for label in labels.iteritems():
                    if options['blacklist']:
                        if label[0] == 'dockplicity' and label[1] == 'false':
                            valid = False
                    else:
                        if label[0] == 'dockplicity' and label[1] == 'true':
                            valid = True
                if valid:
                    services.append({
                        'name': container.attrs['Name'],
                        'host': False,
                        'data_type': data_type,
                        'volumes': get_volumes(platform_type, options, container)
                    })
    return services

def get_volumes(platform_type, options, raw_service):
    volumes = {}
    if platform_type == 'rancher':
        volumes = {}
    else:
        container = raw_service
        labels = container.attrs['Config']['Labels']
        for mount in container.attrs['Mounts']:
            source = mount['Source']
            volume_driver = mount['Driver'] if 'Driver' in mount else 'local'
            if len(source) >= 15 and source[:15] == '/var/lib/docker':
                continue
            if len(source) >= 15 and source[:15] == '/var/run/docker':
                continue
            if volume_driver != options['volume_driver']:
                continue
            destination = ('/volumes/' + mount['Destination'] + '/raw').replace('//', '/')
            volumes[mount['Source']] = {
                'bind': destination,
                'mode': 'rw'
            }
    return volumes

def backup_services(platform_type, services, options):
    environment = {
        'PASSPHRASE': options['passphrase'],
    }
    if 'GS_ACCESS_KEY_ID' in os.environ:
        environment['GS_ACCESS_KEY_ID'] = os.environ['GS_ACCESS_KEY_ID']
    if 'GS_SECRET_ACCESS_KEY' in os.environ:
        environment['GS_SECRET_ACCESS_KEY'] = os.environ['GS_SECRET_ACCESS_KEY']
    for service in services:
        if len(service['volumes']) > 0:
            environment['TARGET_URL'] = (options['target_url'] + '/' + service['name']).replace('//', '/')
            environment['CONTAINER_ID'] = service['name']
            environment['FORCE'] = 'true'
            environment['DATA_TYPE'] = service['data_type']
            service['volumes']['/var/run/docker.sock'] = {
                'bind': '/var/run/docker.sock',
                'mode': 'rw'
            }
            response = client.containers.run(
                image='jamrizzi/dockplicity-restore:latest',
                volume_driver=options['volume_driver'],
                volumes=service['volumes'],
                remove=True,
                privileged=True,
                environment=environment
            )
            print(response)
        else:
            print('No volumes to restore for ' + service['name'])

def get_data_types():
    files = ""
    for file in glob.glob("/docker/config/*.yml"):
        files += open(file, 'r').read()
    settings = yaml.load(files)
    return settings

main()
