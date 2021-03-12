import time
from flask import Flask

from apis import api
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
    api.init_app(app)
    init_settings()

    # background_task()

    return app