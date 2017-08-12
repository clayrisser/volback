from nails.models import get_base_model
from peewee import *
from pydash import _
from passlib.hash import pbkdf2_sha256

BaseModel = get_base_model(__file__)

class User(BaseModel):
    email = CharField()
    password = CharField()

    def hash_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)
