from nails import Nails, config
import api

server = Nails(__name__)

@server.route('/')
def server_index():
    return 'Hello, Nails.py!'

if __name__ == '__main__':
    server.register_app(api.app)
    server.run()
