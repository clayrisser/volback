from config import config, set_app_config, get_config
from flask import Flask, Blueprint, jsonify
from flask_restful import Api
from models import init_database
from logger import init_logger
import exceptions
import imp
import os
import re
import sys

class Nails(Flask):
    def __init__(self, import_name):
        super(self.__class__, self).__init__(import_name)
        app = self

    def run(self, host=None, port=None, debug=None, **options):
        super(self.__class__, self).run(
            host=host if host else config['host'],
            port=port if port else config['port'],
            debug=debug if debug else config['debug']
        )

    def register_app(self, app):
        self.register_blueprint(app)

def handle_exception(e):
    status = 500
    if hasattr(e, 'status') and e.status:
        status = e.status
    response = {
        'message': e.message
    }
    if hasattr(e, 'payload') and e.payload:
        response['payload'] = e.payload
    return jsonify(response), status

def get_controllers(app_name):
    controllers = list()
    controllers_dir = os.path.realpath(config['base_dir'] + '/' + app_name + '/controllers/')
    sys.path.append(controllers_dir)
    return imp.load_source('controllers', controllers_dir + '/__init__.py')

def init_app(filepath, base):
    app_name = ''
    app_dir = ''
    blueprint = None
    matches = re.findall(r'.+(?=.__init__.py)', filepath)
    if len(matches) > 0:
        app_dir = matches[0]
    matches = re.findall(r'[^\/]+(?=.__init__.py)', filepath)
    if len(matches) > 0:
        app_name = matches[0]
    set_app_config(app_name)
    blueprint = Blueprint(
        app_name,
        __name__,
        template_folder=os.path.realpath(config['base_dir'] + '/' + app_name + '/templates/')
    )
    init_logger(app_name, blueprint)
    init_database(app_name, blueprint)
    resource = Api(blueprint)
    controllers = get_controllers(app_name)
    for route, controller_name in config[app_name]['routes'].iteritems():
        controller_name = controller_name.split('.')
        if (len(controller_name) > 1):
            resource.add_resource(getattr(getattr(
                controllers,
                controller_name[0]
            ), controller_name[1]), (base + '/' + route).replace('//', '/').replace('//', '/'))
    @blueprint.errorhandler(Exception)
    def exception(e):
        return handle_exception(e)
    return blueprint
