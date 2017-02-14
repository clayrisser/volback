import os
import docker
import yaml
import glob
import re

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

class Helper:
    def mount_storage(self, **kwargs):
        os.system('''
        mkdir -p /project
        mkdir -p /backup
        echo ''' + kwargs['storage_access_key'] + ':' + kwargs['storage_secret_key'] + ''' > /project/auth.txt
        chmod 600 /project/auth.txt
        ''')
        if kwargs['storage_backend'] == 'gs':
            os.system('''
            s3fs ''' + kwargs['bucket'] + ''' /borg \
            -o nomultipart \
            -o passwd_file=/project/auth.txt \
            -o sigv2 \
            -o url=https://storage.googleapis.com
            ''')
        os.system('mkdir -p ' + kwargs['borg_repo'])

    def get_own_container(self):
        name = os.popen('docker inspect -f \'{{.Name}}\' $HOSTNAME').read()[1:].rstrip()
        container = client.containers.get(name)
        return container

    def get_valid_mounts(self, container):
        mounts = list()
        for mount in container.attrs['Mounts']:
            if len(mount['Destination']) > 8 and mount['Destination'][:9] == '/volumes/':
                mounts.append(mount)
        return mounts

    def get_smart_backup_data(self, **kwargs):
        mounts = client.containers.get(kwargs['container_id']).attrs['Mounts']
        smart_backup_data = {
            'data_type_details': '',
            'raw_dir': '',
            'tmp_dump_dir': '',
            'dump_volume': '',
            'dump_dir': ''
        }
        if kwargs['data_type'] != 'raw':
            data_type_details = self.__get_data_type_details(kwargs['data_type'])
            smart_backup_data['data_type_details'] = data_type_details
            for mount in mounts:
                if mount['Destination'] == data_type_details['data-location']:
                    raw_dir = ('/volumes/' + mount['Destination'] + '/raw').replace('//', '/')
                    tmp_dump_dir = (raw_dir + '/ident_backup').replace('//', '/')
                    dump_volume = ('/volumes/' + mount['Destination']).replace('//', '/')
                    dump_dir = (dump_volume + '/' + kwargs['data_type']).replace('//', '/')
                    smart_backup_data['raw_dir'] = raw_dir
                    smart_backup_data['tmp_dump_dir'] = tmp_dump_dir
                    smart_backup_data['dump_volume'] = dump_volume
                    smart_backup_data['dump_dir'] = dump_dir
        return smart_backup_data

    def __get_data_type_details(self, data_type):
        if data_type != 'raw':
            files = ''
            for file in glob.glob('/app/config/*.yml'):
                files += open(file, 'r').read()
            settings = yaml.load(files)
            setting = settings[data_type]
            setting['backup'] = self.__replace_config_prop_placeholders(setting, 'backup')
            setting['restore'] = self.__replace_config_prop_placeholders(setting, 'restore')
            return setting
        else:
            return 'raw'

    def __replace_config_prop_placeholders(self, setting, prop):
        updated_prop = setting[prop]
        envs = re.findall('(?<=\<)[A-Z\d\-\_]+(?=\>)', updated_prop)
        for env in envs:
            updated_prop = updated_prop.replace('<' + env + '>', os.environ[env] if env in os.environ else '')
        updated_prop = ('/bin/sh -c "' + updated_prop + '"').replace('%DUMP%', setting['data-location'] + '/ident_backup/' + setting['backup-file']).replace('//', '/')
        return updated_prop
