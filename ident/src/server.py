import os
from pkg.borg import Borg
from flask import Flask
from flask_restful import Resource, Api
from pkg.backup import Backup
from pkg.options import Options
from pkg.shared import Shared

options = Options
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

class ContainerBackupTree(Resource):
    def get(self, container, backup):
        backup_tree = borg.get_container_backup_tree(container, backup)
        return backup_tree

class BackupContainer(Resource):
    def post(self, container):
        backup = Backup()
        shared = Shared()
        platform_type = shared.get_platform_type(
            rancher_access_key=options.rancher_access_key,
            rancher_secret_key=options.rancher_secret_key,
            rancher_url=options.rancher_url
        )
        services = shared.get_services(
            blacklist=options.blacklist,
            data_types=options.data_types,
            operation=sys.argv[1],
            own_container=options.own_container,
            platform_type=platform_type,
            rancher_access_key=options.rancher_access_key,
            rancher_secret_key=options.rancher_secret_key,
            rancher_url=options.rancher_url,
            restore_all=options.restore_all,
            service=options.service
        )
        backup.run(
            debug=options.debug,
            encrypt=options.encrypt,
            keep_daily=options.keep_daily,
            keep_hourly=options.keep_hourly,
            keep_monthly=options.keep_monthly,
            keep_weekly=options.keep_weekly,
            keep_within=options.keep_within,
            keep_yearly=options.keep_yearly,
            passphrase=options.passphrase,
            platform_type=platform_type,
            rancher_access_key=options.rancher_access_key,
            rancher_secret_key=options.rancher_secret_key,
            rancher_url=options.rancher_url,
            services=services,
            storage_access_key=options.storage_access_key,
            storage_secret_key=options.storage_secret_key,
            storage_url=options.storage_url,
            storage_volume=options.storage_volume,
            tag=options.tag
        )

api.add_resource(HelloWorld, '/')
api.add_resource(Containers, '/containers')
api.add_resource(ContainerBackups, '/container-backups/<container>')
api.add_resource(ContainersBackups, '/containers-backups')
api.add_resource(ContainerBackupTree, '/container-backup-tree/<container>/<backup>')
api.add_resource(BackupContainer, '/backup-container/<container>')

if __name__ == '__main__':
    app.run(
        host=options.host,
        port=options.port
    )
