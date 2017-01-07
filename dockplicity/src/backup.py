import docker
import time
import random
import json
import glob
import yaml
import socket
import os
import requests
from requests.auth import HTTPBasicAuth
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
        'passphrase': os.environ['PASSPHRASE'] if 'PASSPHRASE' in os.environ else 'hellodocker',
        'backup_type': os.environ['BACKUP_TYPE'] if 'BACKUP_TYPE' in os.environ else 'incr',
        'full_if_older_than': os.environ['FULL_IF_OLDER_THAN'] if 'FULL_IF_OLDER_THAN' in os.environ else '2W',
        'target_url': os.environ['TARGET_URL'] if 'TARGET_URL' in os.environ else 'gs://my_google_bucket',
        'remove_older_than': os.environ['REMOVE_OLDER_THAN'] if 'REMOVE_OLDER_THAN' in os.environ else '6M',
        'tmp_mount': os.environ['TMP_MOUNT'] if 'TMP_MOUNT' in os.environ else '/tmp',
        'encrypt': os.environ['ENCRYPT'] if 'ENCRYPT' in os.environ else 'false',
        'remove_all_but_n_full': os.environ['REMOVE_ALL_BUT_N_FULL'] if 'REMOVE_ALL_BUT_N_FULL' in os.environ else '12',
        'blacklist': False if os.environ['BLACKLIST'] != 'true' else True,
        'service': False if os.environ['SERVICE'] == '' else os.environ['SERVICE'],
        'data_types': get_data_types(),
        'remove_all_inc_but_of_n_full': os.environ['REMOVE_ALL_INC_BUT_OF_N_FULL'] if 'REMOVE_ALL_INC_BUT_OF_N_FULL' in os.environ else '144'
    }

def get_platform_type(options):
    if options['rancher_url'] or options['rancher_access_key'] or options['rancher_secret_key']:
        if options['rancher_url'] and options['rancher_access_key'] and options['rancher_secret_key']:
            return 'rancher'
        else:
            exit('You are missing RANCHER_URL, RANCHER_ACCESS_KEY, or RANCHER_SECRET_KEY')
    else:
        return 'docker'

def get_services(platform_type, options):
    services = list()
    if platform_type == 'rancher':
        if options['service']:
            for service in rancher_call(options, '/services')['data']:
                if service['name'] == options['service']:
                    if service['instanceIds']:
                        container = rancher_call(options, '/containers/' + random.choice(service['instanceIds']))
                        data_type = 'raw'
                        for key, item in options['data_types'].iteritems():
                            image = container['data']['dockerContainer']['Image']
                            if ':' in image:
                                image = image[:image.index(':')]
                            if image == key:
                                data_type = key
                        services.append({
                            'name': service['name'],
                            'container': container['data']['dockerContainer']['Names'][0][1:],
                            'host': container['hostId'],
                            'data_type': data_type,
                            'mounts': get_mounts(platform_type, options, container)
                        })
        else:
            for service in rancher_call(options, '/services')['data']:
                if service['instanceIds']:
                    container = rancher_call(options, '/containers/' + random.choice(service['instanceIds']))
                    data_type = 'raw'
                    for key, item in options['data_types'].iteritems():
                        image = container['data']['dockerContainer']['Image']
                        if ':' in image:
                            image = image[:image.index(':')]
                        if image == key:
                            data_type = key
                    valid = False
                    if options['blacklist']:
                        valid = True
                    labels = container['data']['dockerContainer']['Labels']
                    for label in labels.iteritems():
                        if options['blacklist']:
                            if label[0] == 'dockplicity' and label[1] == 'false':
                                valid = False
                        else:
                            if label[0] == 'dockplicity' and label[1] == 'true':
                                valid = True
                    if valid:
                        services.append({
                            'name': service['name'],
                            'container': container['data']['dockerContainer']['Names'][0][1:],
                            'host': container['hostId'],
                            'data_type': data_type,
                            'mounts': get_mounts(platform_type, options, container)
                        })
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
                'name': container.attrs['Name'][1:],
                'container': container.attrs['Name'][1:],
                'host': False,
                'data_type': data_type,
                'mounts': get_mounts(platform_type, options, container)
            })
        else:
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
                        'name': container.attrs['Name'][1:],
                        'container': container.attrs['Name'][1:],
                        'host': False,
                        'data_type': data_type,
                        'mounts': get_mounts(platform_type, options, container)
                    })
    return services

def get_mounts(platform_type, options, container):
    mounts = list()
    all_mounts = {}
    if platform_type == 'rancher':
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
        destination = ('/volumes/' + mount['Destination'] + '/raw').replace('//', '/')
        mounts.append({
            'source': source,
            'destination': destination,
            'origional_destination': mount['Destination'],
            'driver': driver,
            'mode': 'rw'
        })
    return mounts

def backup_services(platform_type, services, options):
    if len(services) <= 0:
        exit('No services to backup')
    environment = {
        'PASSPHRASE': options['passphrase'],
        'BACKUP_TYPE': options['backup_type'],
        'REMOVE_ALL_BUT_N_FULL': options['remove_all_but_n_full'],
        'REMOVE_ALL_INC_BUT_OF_N_FULL': options['remove_all_inc_but_of_n_full'],
        'REMOVE_OLDER_THAN': options['remove_older_than'],
        'FULL_IF_OLDER_THAN': options['full_if_older_than'],
        'TMPDIR': '/tmp/duplicity',
        'ENCRYPT': options['encrypt']
    }
    if 'GS_ACCESS_KEY_ID' in os.environ:
        environment['GS_ACCESS_KEY_ID'] = os.environ['GS_ACCESS_KEY_ID']
    if 'GS_SECRET_ACCESS_KEY' in os.environ:
        environment['GS_SECRET_ACCESS_KEY'] = os.environ['GS_SECRET_ACCESS_KEY']
    if platform_type == 'rancher':
        os.popen('''
        (echo ''' + options['rancher_url'] + '''; \
        echo ''' + options['rancher_access_key'] + '''; \
        echo ''' + options['rancher_secret_key'] + ''') | rancher config
        ''')
    for service in services:
        if len(service['mounts']) > 0:
            success = False
            environment['TARGET_URL'] = options['target_url'] + ('/' + service['name']).replace('//', '/')
            environment['CONTAINER_ID'] = service['container']
            environment['DATA_TYPE'] = service['data_type']
            if platform_type == 'rancher':
                command = 'rancher --host ' + service['host'] + ' docker run --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock -v ' + options['tmp_mount'] + ':/tmp/duplicity'
                for key, env in environment.iteritems():
                    command += ' -e ' + key + '=' + env
                for mount in service['mounts']:
                    command += ' -v ' + mount['source'] + ':' + mount['destination']
                command += ' jamrizzi/dockplicity-backup:latest'
                print(command)
                res = os.system(command)
                if (res == 0):
                    success = True
            else:
                volumes = {}
                for mount in service['mounts']:
                    volumes[mount['source']] = {
                        'bind': mount['destination'],
                        'mode': mount['mode']
                    }
                volumes['/var/run/docker.sock'] = {
                    'bind': '/var/run/docker.sock',
                    'mode': 'rw'
                }
                volumes[options['tmp_mount']] = {
                    'bind': '/tmp/duplicity',
                    'mode': 'rw'
                }
                try:
                    response = client.containers.run(
                        image='jamrizzi/dockplicity-backup:latest',
                        volumes=volumes,
                        remove=True,
                        privileged=True,
                        environment=environment
                    )
                    success = True
                except:
                    success = False
            if (success):
                print('\n' + service['name'] + ' ~' + service['data_type'] + ': SUCCESS\n----------------------------')
            else:
                print('\n' + service['name'] + ' ~' + service['data_type'] + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                print('    - ' + mount['source'] + ':' + mount['origional_destination'] + ' (' + mount['driver'] + ')' + ' ~' + service['data_type'])
            time.sleep(1)
        else:
            print('\n' + service['name'] + ': NO VOLUMES\n-----------------------------')

def get_data_types():
    files = ""
    for file in glob.glob("/docker/config/*.yml"):
        files += open(file, 'r').read()
    settings = yaml.load(files)
    return settings

def rancher_call(options, call):
    r = requests.get(options['rancher_url'] + '/v2-beta/' + call, auth=HTTPBasicAuth(options['rancher_access_key'], options['rancher_secret_key']), headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    return r.json()

main()
