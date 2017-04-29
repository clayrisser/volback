import os
from pkg.borg import Borg
from flask import Flask
from flask_restful import Resource, Api

options = {
    'debug': True if os.environ['DEBUG'] == 'true' else False,
    'host': os.environ['HOST'] if 'HOST' in os.environ else '0.0.0.0',
    'port': os.environ['PORT'] if 'PORT' in os.environ else 8888
}

app = Flask(__name__)
api = Api(app)
borg = Borg('/backup')

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'ident'}

class Containers(Resource):
    def get(self):
        containers = borg.get_containers()
        return containers

class ContainerBackups(Resource):
    def get(self, container):
        container_backups = borg.get_container_backups(container)
        return container_backups

class ContainersBackups(Resource):
    def get(self):
        containers_backups = borg.get_containers_backups()
        return containers_backups

api.add_resource(HelloWorld, '/')
api.add_resource(Containers, '/containers')
api.add_resource(ContainerBackups, '/container-backups/<container>')
api.add_resource(ContainersBackups, '/containers-backups')

if __name__ == '__main__':
    app.run(
        host=options['host'],
        port=options['port']
    )
