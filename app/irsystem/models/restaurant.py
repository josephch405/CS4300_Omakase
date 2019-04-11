from . import *

class Restaurant(Base):
  __tablename__ = 'restaurants'

  name           = db.Column(db.String(128), nullable=False, unique=True)
  url            = db.Column(db.String(128), nullable=False, unique=True)

  def __init__(self, **kwargs):
    self.name           = kwargs.get('name', None)
    self.url            = kwargs.get('url', None)

  def __repr__(self):
    return str(self.__dict__)


class RestaurantSchema(ModelSchema):
  class Meta:
    model = Restaurant
