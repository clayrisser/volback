from nails import config
from peewee import *
import datetime
import imp
import os
import pydash as _
import re
import sys

databases = {}

def get_database(app_name):
    if app_name not in databases:
        database = config['database']
        if 'database' in config[app_name] and 'driver' in config[app_name]['database']:
            database = config[app_name]['database']
        if database['driver'] == 'postgres':
            databases[app_name] = PostgresqlDatabase(
                'postgres',
                user=database['user'],
                password=database['password'],
                host=database['host'],
                port=database['port']
            )
        if database['driver'] == 'sqlite':
            databases[app_name] = SqliteDatabase(database['file'])
    if app_name not in databases:
        raise ValueError('Database driver \'' + database['driver'] + '\' does not exist')
    return databases[app_name]

def get_models(app_name):
    models = list()
    models_list = list()
    models_dir = os.path.realpath(config['base_dir'] + '/' + app_name + '/models/')
    sys.path.append(models_dir)
    models_import = imp.load_source('models', models_dir + '/__init__.py')
    for model_name in _.keys(models_import):
        matches = re.findall(r'^[A-Z].+', model_name)
        if len(matches) > 0:
            models.append(getattr(models_import, model_name))
    return models

def init_database(app_name, blueprint):
    db = get_database(app_name)
    db.connect()
    models = get_models(app_name)
    db.create_tables(models, safe=True)
    db.close()
    @blueprint.before_request
    def db_connect():
        db.connect()
    @blueprint.teardown_request
    def db_close(exc):
        if not db.is_closed():
            db.close()

def get_base_model(filepath):
    app_name = ''
    matches = re.findall(r'[^\/]+(?=\/models\/[^\/]+_model.pyc?$)', filepath)
    if len(matches) > 0:
        app_name = matches[0]
    class BaseModel(Model):
        created_at = DateTimeField(default=datetime.datetime.now)
        class Meta:
            database = databases[app_name]
    return BaseModel
