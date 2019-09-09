# project/server/__init__.py

import os
from project.server.auth.views import auth_blueprint
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)
app.register_blueprint(auth_blueprint)
