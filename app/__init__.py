import threading

import socketio
from flask import Flask

from app.util import config

# Define the WSGI application object
app = Flask(__name__)
sio = socketio.Client()

# Configurations
app.config.from_object(config)

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
threading.Thread(target=api.job_handler, daemon=True).start()
