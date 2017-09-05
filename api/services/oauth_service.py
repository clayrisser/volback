from flask_oauthlib.client import OAuth
from flask import session
from api import app

oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key='3d62ecb18190c4585fb0',
    consumer_secret='965323453efc86ca2575069819ccb1b8e9dc99fd',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@github.tokengetter
def github_tokengetter():
    return session.get('github_token')

def github_to_user(github_user):
    user = {
        'avatar': github_user['avatar_url'],
        'username': github_user['login'],
        'display_name': github_user['name'],
        'github': github_user['login']
    }
    if 'email' in github_user and github_user['email']:
        user['email'] = github_user['email']
    return user
