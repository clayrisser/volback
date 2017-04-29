import os

class Borg:
    def __init__(self):
        return

    def __run(self, command):
        return os.environ('borg ' + command)

    def list(self):
        res = __run(self, 'list')
