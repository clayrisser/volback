import os

class Borg:
    def __init__(self, borg_dir):
        self.borg_dir = borg_dir

    def __run(self, command):
        return os.popen('cd ' + self.borg_dir + ' && ' + command).read()

    def __borg(self, command):
        return self.__run('borg ' + command)

    def get_containers(self):
        return os.listdir(self.borg_dir)

    def get_container_backups(self, container):
        string = self.__borg('list ' + container)
        backups = string.split('\n')
        del backups[len(backups) - 1]
        sanatized_backups = list()
        for backup in backups:
            backup = backup.split(' ')[0]
            sanatized_backups.append(backup)
        return sanatized_backups

    def get_containers_backups(self):
        containers = self.get_containers()
        containers_backups = {}
        for container in containers:
            containers_backups[container] = self.get_container_backups(container)
        return containers_backups
