# Import flask and template operators
from flask import Flask, wrappers
from flask_cors import CORS

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Migration Module
from flask_migrate import Migrate

# Import Util Modules
# from app.util.responses import NotFoundError

# Define the WSGI application object
app = Flask(__name__)
CORS(app)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found (error: Exception) -> wrappers.Response:
#    return NotFoundError

# Import a module / component using its blueprint handler variable (mod_auth)

from app.models.device import Device
from app.models.public_keys import OPKey

from app.modules.auth.controller import mod_auth as auth_module
from app.modules.user.controller import mod_user as user_module

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(user_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy

db.create_all()