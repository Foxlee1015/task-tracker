import time
from flask import Flask
from flask_cors import CORS

from apis import blueprint as api
from core.db import init_db, backup_db
from core.errors import DbConnectError

def init_settings():
    try:
        pass
        init_db()
    except DbConnectError as e:
        print(e)

# thread
def background_task():
    while True:
        print("background_task")
        # backup_db()

def create_app():
    app = Flask(__name__)
    CORS(app)
    #cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(api, url_prefix='/api')
    # api.init_app(app) 
    # https://flask-restplus.readthedocs.io/en/stable/scaling.html
    # Calling Api.init_app() is not required here because registering the blueprint with the app takes care of setting up the routing for the application.
    init_settings()

    # background_task()

    return app
