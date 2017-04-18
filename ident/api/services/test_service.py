from api.config import config

def hello_world():
    return {
        'message': 'Hello, world!',
        'fun_facts': config.fun_facts
    }
