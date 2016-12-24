import docker
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
        'backup_type': os.environ['BACKUP_TYPE'] if 'BACKUP_TYPE' in os.environ else 'incr',
        'full_if_older_than': os.environ['FULL_IF_OLDER_THAN'] if 'FULL_IF_OLDER_THAN' in os.environ else '2W',
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'remove_older_than': os.environ['REMOVE_OLDER_THAN'] if 'REMOVE_OLDER_THAN' in os.environ else '6M',
        'remove_all_but_n_full': os.environ['REMOVE_ALL_BUT_N_FULL'] if 'REMOVE_ALL_BUT_N_FULL' in os.environ else '12',
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
        for container in client.containers.list():
            labels = container.attrs['Config']['Labels']
            for label in labels.iteritems():
                if label[0] == 'dockplicity' and label[1] == 'true':
                    services.append({
                        'name': container.attrs['Name'],
                        'host': False,
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
            destination = ('/volumes/' + mount['Source'] + '/raw').replace('//', '/')
            volumes[mount['Source']] = {
                'bind': destination,
                'mode': 'rw'
            }
    return volumes

def backup_services(platform_type, services, options):
    environment = {
        'PASSPHRASE': options['passphrase'],
        'BACKUP_TYPE': options['backup_type'],
        'REMOVE_ALL_BUT_N_FULL': options['remove_all_but_n_full'],
        'REMOVE_ALL_INC_BUT_OF_N_FULL': options['remove_all_inc_but_of_n_full'],
        'REMOVE_OLDER_THAN': options['remove_older_than'],
        'FULL_IF_OLDER_THAN': options['full_if_older_than']
    }
    if 'GS_ACCESS_KEY_ID' in os.environ:
        environment['GS_ACCESS_KEY_ID'] = os.environ['GS_ACCESS_KEY_ID']
    if 'GS_SECRET_ACCESS_KEY' in os.environ:
        environment['GS_SECRET_ACCESS_KEY'] = os.environ['GS_SECRET_ACCESS_KEY']
    for service in services:
        if len(service['volumes']) > 0:
            environment['TARGET_URL'] = (options['target_url'] + '/' + service['name']).replace('//', '/')
            print(environment)
            print(service['volumes'])
            print(options['volume_driver'])
            response = client.containers.run(
                image='jamrizzi/dockplicity-backup',
                volume_driver=options['volume_driver'],
                volumes=service['volumes'],
                environment=environment
            )
            print(response)
        else:
            print('No volumes to backup for ' + service['name'])

main()
