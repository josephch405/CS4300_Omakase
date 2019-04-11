from . import *

class User(Base):
  __tablename__ = 'users'

  username        = db.Column(db.String(128), nullable =False, unique =True)
  password_digest = db.Column(db.String(192), nullable =False)

  def __init__(self, **kwargs):
    self.username        = kwargs.get('username', None)
    self.password_digest = generate_password_hash(kwargs.get('password'), None)

  def __repr__(self):
    return str(self.__dict__)


class UserSchema(ModelSchema):
  class Meta:
    model = User
