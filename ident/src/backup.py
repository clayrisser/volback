import docker
import time
import random
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from helper import Helper
from shared import Shared

client = docker.DockerClient(base_url='unix://var/run/docker.sock')
helper = Helper()
shared = Shared()

def main():
    options = get_options()
    mount_storage(options)
    platform_type = get_platform_type(options)
    services = get_services(platform_type, options)
    backup_services(platform_type, services, options)

def backup_services(platform_type, services, options):
    if len(services) <= 0:
        exit('No services to backup')
    environment = {
        'PASSPHRASE': options['passphrase'],
        'ENCRYPT': options['encrypt'],
        'KEEP_WITHIN': options['keep_within'],
        'HOURLY': options['hourly'],
        'DAILY': options['daily'],
        'WEEKLY': options['weekly'],
        'MONTHLY': options['monthly'],
        'YEARLY': options['yearly'],
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
                command += ' jamrizzi/ident-backup:latest'
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
                        image='jamrizzi/ident-backup:latest',
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
                print('\n' + service['name'] + data_type_pretty + ': SUCCESS\n----------------------------')
            else:
                print('\n' + service['name'] + data_type_pretty + ': FAILED\n-----------------------------')
            for mount in service['mounts']:
                driver_pretty = '' if mount['driver'] == 'local' else ' (' + mount['driver'] + ')'
                print('    - ' + mount['source'] + ':' + mount['origional_destination'] + driver_pretty + data_type_pretty)
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
