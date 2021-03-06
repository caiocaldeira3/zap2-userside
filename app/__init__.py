import socketio
import threading

# Import flask and template operators
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Migration Module
from flask_migrate import Migrate

# Import Util Modules

# from app.util.responses import NotFoundError

# Define the WSGI application object
app = Flask(__name__)
sio = socketio.Client()

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
from app.util.jobs import JobQueue
job_queue = JobQueue()

from app.util.api import Api
api = Api()

import app.modules.auth.events
import app.modules.user.events

# Register blueprint(s)
# ..

# Build the database:
# This will create the database file using SQLAlchemy

db.create_all()
threading.Thread(target=api.job_handler, daemon=True).start()