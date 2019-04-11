from . import *
from .restaurant import *

class MenuItem(Base):
  __tablename__ = 'menu_items'

  name           = db.Column(db.String(128), nullable=False, unique=True)
  category       = db.Column(db.String(128), nullable=False)
  price          = db.Column(db.Float(), nullable=False)
  restaurant_id  = db.Column(db.Integer(), db.ForeignKey(Restaurant.id))

  restaurant     = db.relationship('Restaurant', foreign_keys='MenuItem.restaurant_id')

  def __init__(self, **kwargs):
    self.name           = kwargs.get('name', None)
    self.category       = kwargs.get('category', None)
    self.price          = kwargs.get('price', None)
    self.restaurant_id  = kwargs.get('restaurant_id', None)

  def __repr__(self):
    return str(self.__dict__)


class MenuItemSchema(ModelSchema):
  class Meta:
    model = MenuItem
