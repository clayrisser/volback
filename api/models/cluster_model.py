from nails.models import get_base_model
from peewee import *

BaseModel = get_base_model(__file__)

class Cluster(BaseModel):
    name = CharField()
    provider = CharField()
