from nails.models import get_base_model
from peewee import *
from pydash import _

BaseModel = get_base_model(__file__)

class UserModel(BaseModel):
    title = CharField()
