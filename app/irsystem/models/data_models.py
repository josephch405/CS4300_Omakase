from . import *

class MenuItem(Base):
  __tablename__ = 'menu_items'

  name           = db.Column(db.String(128), nullable=False)
  category       = db.Column(db.String(128), nullable=False)
  price          = db.Column(db.Float(), nullable=False)
  restaurant_id  = db.Column(db.Integer(), db.ForeignKey('Restaurant.id'), nullable=False)

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

class Restaurant(Base):
  __tablename__ = 'restaurants'

  name           = db.Column(db.String(128), nullable=False, unique=True)
  url            = db.Column(db.String(128), nullable=False, unique=True)

  menu_items     = db.relationship('MenuItem', backref='restaurant', lazy=True)

  def __init__(self, **kwargs):
    self.name           = kwargs.get('name', None)
    self.url            = kwargs.get('url', None)

  def __repr__(self):
    return str(self.__dict__)


class RestaurantSchema(ModelSchema):
  class Meta:
    model = Restaurant
