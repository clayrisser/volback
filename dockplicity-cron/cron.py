import docker
import socket
import os
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def main():
    options = get_options()
    response = backup_volumes(options)
    print(response)

def get_options():
    return {
        'volume_driver': os.environ['VOLUME_DRIVER'] if 'VOLUME_DRIVER' in os.environ else 'local',
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'backup_type': os.environ['BACKUP_TYPE'] if 'BACKUP_TYPE' in os.environ else 'incr',
        'full_if_older_than': os.environ['FULL_IF_OLDER_THAN'] if 'FULL_IF_OLDER_THAN' in os.environ else '2W',
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'remove_older_than': os.environ['REMOVE_OLDER_THAN'] if 'REMOVE_OLDER_THAN' in os.environ else '6M',
        'remove_all_but_n_full': os.environ['REMOVE_ALL_BUT_N_FULL'] if 'REMOVE_ALL_BUT_N_FULL' in os.environ else '12',
        'remove_all_inc_but_of_n_full': os.environ['REMOVE_ALL_INC_BUT_OF_N_FULL'] if 'REMOVE_ALL_INC_BUT_OF_N_FULL' in os.environ else '144'
    }

def backup_volumes(options):
    containers = get_containers_to_backup(options)
    volumes = {}
    environement = {
        'PASSPHRASE': options['passphrase'],
        'BACKUP_TYPE': options['backup_type'],
        'TARGET_URL': options['target_url'],
        'REMOVE_ALL_BUT_N_FULL': options['remove_all_but_n_full'],
        'REMOVE_ALL_INC_BUT_OF_N_FULL': options['remove_all_inc_but_of_n_full'],
        'REMOVE_OLDER_THAN': options['remove_older_than'],
        'FULL_IF_OLDER_THAN': options['full_if_older_than']
    }
    for container in containers:
        volumes = dict(volumes.items() + get_volumes_to_backup(container, options).items())
    if len(volumes) > 0:
        return client.containers.run(
            image='jamrizzi/dockplicity-backup',
            command='ls /volumes',
            volume_driver=options['volume_driver'],
            volumes=volumes,
            environment=environment
        )
    else:
        return 'No volumes to back up'

def get_containers_to_backup(options):
    containers = client.containers.list()
    containers_to_backup = list()
    for container in containers:
        volume_driver = container.attrs['HostConfig']['VolumeDriver'] if 'VolumeDriver' in container.attrs['HostConfig'] : 'local'
        if options['volume_driver'] != volume_driver:
            continue
        labels = container.attrs['Config']['Labels']
        for label in labels.iteritems():
            if label[0] == 'dockplicity' and label[1] == 'true':
                containers_to_backup.append(container)
    return containers_to_backup

def get_volumes_to_backup(container, options):
    volumes = {}
    labels = container.attrs['Config']['Labels']
    name = container.attrs['Name']
    for label in labels.iteritems():
        if label[0] == 'io.rancher.stack_service.name':
            name = label[1]
    for mount in container.attrs['Mounts']:
        source = mount['Source']
        driver = mount['Driver'] if 'Driver' in mount else 'local'
        if len(source) >= 15 and source[:15] == '/var/lib/docker':
            continue
        if len(source) >= 15 and source[:15] == '/var/run/docker':
            continue
        if driver != options['volume_driver']:
            continue
        destination = '/volumes/' + name + '/' + mount['Source']
        destination = destination.replace('//', '/')
        volumes[mount['Source']] = {
            'bind': destination,
            'mode': 'rw'
        }
    return volumes

main()
