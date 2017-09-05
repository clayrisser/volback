from nails.models import get_base_model
from peewee import *
from pydash import _
from passlib.hash import pbkdf2_sha256

BaseModel = get_base_model(__file__)

class User(BaseModel):
    first_name = CharField()
    last_name = CharField(default='')
    display_name = CharField()
    username = CharField()
    email = CharField(default='')
    avatar = CharField(default='')
    password = CharField(default='')
    github = CharField(default='')
    role = CharField(default='user')

    def hash_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)
