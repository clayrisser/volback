from api.models import UserModel
from nails import Controller

class User(Controller):
    def get(self):
        return 'a user'

class UserList(Controller):
    def get(self):
        return 'a list of users'
