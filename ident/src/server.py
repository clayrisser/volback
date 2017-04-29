import os
from flask import Flask
from flask_restful import Resource, Api

options = {
    'debug': True if os.environ['DEBUG'] == 'true' else False,
    'host': os.environ['HOST'] if 'HOST' in os.environ else '0.0.0.0',
    'port': os.environ['PORT'] if 'PORT' in os.environ else 8888
}

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(
        host=options['host'],
        port=options['port']
    )
