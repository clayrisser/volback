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
    restore_services(platform_type, services, options)

def get_options():
    return {
        'rancher_url': False if os.environ['RANCHER_URL'] == '' else os.environ['RANCHER_URL'],
        'rancher_access_key': False if os.environ['RANCHER_ACCESS_KEY'] == '' else os.environ['RANCHER_ACCESS_KEY'],
        'rancher_secret_key': False if os.environ['RANCHER_SECRET_KEY'] == '' else os.environ['RANCHER_SECRET_KEY'],
        'passphrase': os.environ['PASSPHRASE'],
        'storage_url': os.environ['STORAGE_URL'],
        'blacklist': False if os.environ['BLACKLIST'] != 'true' else True,
        'encrypt': os.environ['ENCRYPT'],
        'service': False if os.environ['SERVICE'] == '' else os.environ['SERVICE'],
        'restore_all': True if os.environ['RESTORE_ALL'] == 'true' else False,
        'storage_volume': os.environ['STORAGE_VOLUME'] if 'STORAGE_VOLUME' in os.environ else False,
        'storage_access_key': os.environ['STORAGE_ACCESS_KEY'],
        'storage_secret_key': os.environ['STORAGE_SECRET_KEY'],
        'time': False if os.environ['TIME'] == '' else os.environ['TIME'],
        'data_types': get_data_types()
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
        elif options['restore_all']:
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

def restore_services(platform_type, services, options):
    if len(services) <= 0:
        exit('No services to restore')
    environment = {
        'PASSPHRASE': options['passphrase'],
        'ENCRYPT': options['encrypt'],
        'TIME': options['time'],
        'STORAGE_ACCESS_KEY': options['storage_access_key'],
        'STORAGE_SECRET_KEY': options['storage_secret_key'],
        'STORAGE_URL': options['storage_url']
    }
    if platform_type == 'rancher':
        os.popen('''
        (echo ''' + options['rancher_url'] + '''; \
        echo ''' + options['rancher_access_key'] + '''; \
        echo ''' + options['rancher_secret_key'] + ''') | rancher config
        ''')
    for service in services:
        if len(service['mounts']) > 0:
            success = False
            environment['CONTAINER_ID'] = service['container']
            environment['DATA_TYPE'] = service['data_type']
            environment['SERVICE'] = service['name']
            if platform_type == 'rancher':
                storage_volume = ''
                if options['storage_volume']:
                    storage_volume = ' -v ' + options['storage_volume'] + ':/borg'
                command = 'rancher --host ' + service['host'] + ' docker run --rm --privileged -v /var/run/docker.sock:/var/run/docker.sock' + storage_volume
                for key, env in environment.iteritems():
                    command += ' -e ' + key + '=' + env
                for mount in service['mounts']:
                    command += ' -v ' + mount['source'] + ':' + mount['destination']
                command += ' jamrizzi/dockplicity-restore:latest'
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
                if options['storage_volume']:
                    volumes[options['storage_volume']] = {
                        'bind': '/borg',
                        'mode': 'rw'
                    }
                try:
                    response = client.containers.run(
                        image='jamrizzi/dockplicity-restore:latest',
                        volumes=volumes,
                        remove=True,
                        privileged=True,
                        environment=environment
                    )
                    success = True
                except:
                    success = False
            if (success):
                print('\n' + service['name'] + ': SUCCESS\n----------------------------')
            else:
                print('\n' + service['name'] + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                print('    - ' + mount['source'] + ':' + mount['origional_destination'])
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
