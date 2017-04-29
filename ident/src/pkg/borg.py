import os
import urllib2

class Borg:
    def __init__(self, borg_dir):
        self.mounted = False
        self.borg_dir = borg_dir

    def __run(self, command):
        return os.popen('cd ' + self.borg_dir + ' && ' + command).read()

    def __borg(self, repo, command):
        os.environ['BORG_REPO'] = self.borg_dir + '/' + repo
        return self.__run('borg ' + command)

    def get_containers(self):
        return os.listdir(self.borg_dir)

    def get_container_backups(self, container):
        string = self.__borg(container, 'list')
        backups = string.split('\n')
        del backups[len(backups) - 1]
        sanatized_backups = list()
        for backup in backups:
            backup = backup.split(' ')[0]
            backup = self.__encrypt_backup_name(backup)
            sanatized_backups.append(backup)
        return sanatized_backups

    def get_containers_backups(self):
        containers = self.get_containers()
        containers_backups = {}
        for container in containers:
            containers_backups[container] = self.get_container_backups(container)
        return containers_backups

    def __decrypt_backup_name(self, backup):
        return urllib2.unquote(backup).decode('utf8')

    def __encrypt_backup_name(self, backup):
        return urllib2.quote(backup)

    def __get_directory_tree(self, path):
        result = {'name': os.path.basename(path)}
        if os.path.isdir(path):
            result['type'] = 'd'
            result['children'] = [self.__get_directory_tree(os.path.join(path, x)) for x in os.listdir(path)]
        else:
            result['type'] = 'f'
        return result

    def __mount_backup(self, container, backup):
        os.mkdir('/mnt/' + container)
        self.__borg(container, 'mount ::' + backup + ' /mnt/' + container)
        self.mounted = True

    def get_backup_tree(self, container, backup):
        backup = self.__decrypt_backup_name(backup)
        if not self.mounted:
            self.__mount_backup(container, backup)
        return self.__get_directory_tree('/mnt/' + container)
