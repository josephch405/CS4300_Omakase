# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
import sqlite3
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Configure app
socketio = SocketIO()
app = Flask(__name__)
app.config.from_object(os.environ.get("APP_SETTINGS", "config.DevelopmentConfig"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# DB
db_path = os.path.join(
  os.path.dirname(os.path.realpath(__file__)),
  "../data/omakase_db.sqlite3"
)
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row

# create schema if uninitialized
# c = db.cursor()
# c.executescript("""
# CREATE TABLE IF NOT EXISTS users (
#   user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#   username TEXT UNIQUE NOT NULL,
#   hashed_pw TEXT NOT NULL 
# );

# CREATE TABLE IF NOT EXISTS preferences (
#   user_id INTEGER,
#   restaurant TEXT,
#   menu_item TEXT,
#   rating INTEGER,
#   FOREIGN KEY(user_id) REFERENCES users(user_id)
# );
# """)

# Import + Register Blueprints
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404
