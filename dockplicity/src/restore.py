import docker
import re
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
    mount_storage(options)
    platform_type = get_platform_type(options)
    services = get_services(platform_type, options)
    restore_services(platform_type, services, options)

def get_options():
    options = {
        'storage_url': os.environ['STORAGE_URL'],
        'time': os.environ['TIME']
    }
    _time = 0
    if options['time'][len(options['time']) - 1:] == 'S':
        _time = int(time.time()) - int(options['time'][:len(options['time']) - 1])
    elif options['time'][len(options['time']) - 1:] == 'M':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60)
    elif options['time'][len(options['time']) - 1:] == 'H':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60)
    elif options['time'][len(options['time']) - 1:] == 'd':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24)
    elif options['time'][len(options['time']) - 1:] == 'w':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24 * 7)
    elif options['time'][len(options['time']) - 1:] == 'm':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24 * 265.25 / 12)
    elif options['time'][len(options['time']) - 1:] == 'y':
        _time = int(time.time()) - int(int(options['time'][:len(options['time']) - 1]) * 60 * 60 * 24 * 265.25)
    elif options['time'] == '':
        _time = int(time.time())
    else:
        _time = int(options['time'])
    storage_backend = False
    bucket = ''
    if options['storage_url'] != '':
        storage_backend = options['storage_url'][:options['storage_url'].index(':')]
        bucket = options['storage_url'][options['storage_url'].index(':') + 3:]
    own_container = get_own_container()
    storage_volume = False
    for mount in own_container.attrs['Mounts']:
        if mount['Destination'] == '/borg':
            storage_volume = mount['Source']
    return {
        'rancher_url': False if os.environ['RANCHER_URL'] == '' else os.environ['RANCHER_URL'],
        'rancher_access_key': False if os.environ['RANCHER_ACCESS_KEY'] == '' else os.environ['RANCHER_ACCESS_KEY'],
        'rancher_secret_key': False if os.environ['RANCHER_SECRET_KEY'] == '' else os.environ['RANCHER_SECRET_KEY'],
        'passphrase': os.environ['PASSPHRASE'],
        'storage_url': os.environ['STORAGE_URL'],
        'blacklist': False if os.environ['BLACKLIST'] != 'true' else True,
        'storage_backend': storage_backend,
        'bucket': bucket,
        'encrypt': os.environ['ENCRYPT'],
        'service': False if os.environ['SERVICE'] == '' else os.environ['SERVICE'],
        'restore_all': True if os.environ['RESTORE_ALL'] == 'true' else False,
        'storage_volume': storage_volume,
        'storage_access_key': os.environ['STORAGE_ACCESS_KEY'],
        'storage_secret_key': os.environ['STORAGE_SECRET_KEY'],
        'time': _time,
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
        if mount['Destination'] == '/borg':
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

def mount_storage(options):
    os.system('''
    mkdir -p /project
    echo ''' + options['storage_access_key'] + ':' + options['storage_secret_key'] + ''' > /project/auth.txt
    chmod 600 /project/auth.txt
    ''')
    if options['storage_backend'] == 'gs':
        os.system('''
        s3fs ''' + options['bucket'] + ''' /borg \
        -o nomultipart \
        -o passwd_file=/project/auth.txt \
        -o sigv2 \
        -o url=https://storage.googleapis.com
        ''')

def restore_services(platform_type, services, options):
    if len(services) <= 0:
        exit('No services to restore')
    environment = {
        'PASSPHRASE': options['passphrase'],
        'ENCRYPT': options['encrypt'],
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
            timestamp = get_time(options, service)
            environment['TIME'] = timestamp
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

            data_type_pretty = '' if service['data_type'] == 'raw' else ' ~' + service['data_type']
            if (success):
                print('\n' + service['name'] + data_type_pretty + ' (' + time.strftime("%B %d, %Y %I:%M %p %Z", time.localtime(int(timestamp))) + '): SUCCESS\n----------------------------')
            else:
                print('\n' + service['name'] + data_type_pretty + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                driver_pretty = '' if mount['driver'] == 'local' else ' (' + mount['driver'] + ')'
                print('    - ' + mount['source'] + ':' + mount['origional_destination'] + driver_pretty + data_type_pretty)
        else:
            print('\n' + service['name'] + ': NO VOLUMES\n-----------------------------')

def get_time(options, service):
    os.environ['BORG_PASSPHRASE'] = os.environ['PASSPHRASE']
    borg_repo = '/borg/' + service['name']
    if os.path.isdir(borg_repo):
        timestamp = -1
        backups = filter(None, os.popen('borg list ' + borg_repo).read().split('\n'))
        for backup in backups:
            _timestamp = int(re.findall('(?<=\-)[\d]+(?=[" "])', backup)[0])
            if (_timestamp <= options['time']):
                if (_timestamp > timestamp):
                    timestamp = _timestamp
            elif (timestamp == -1 or _timestamp < timestamp):
                timestamp = _timestamp
        return str(timestamp)
    else:
        return str(options['time'])

def get_own_container():
    ip = socket.gethostbyname(socket.gethostname())
    for container in client.containers.list():
        if (container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress'] == ip):
            return container

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
