from flask import Blueprint
from flask_restplus import Api
import jwt

from .tasks import api as tasks
from .links import api as links
from .logs import api as logs
from .sessions import api as sessions
from .tokens import api as tokens
from .users import api as users


blueprint = Blueprint('api', __name__)
api = Api(
    blueprint,
    title='Task tracker API',
    version='1.0',
    description='A description'
)


api.add_namespace(tasks)
api.add_namespace(links)
api.add_namespace(logs)
api.add_namespace(sessions)
api.add_namespace(users)
api.add_namespace(tokens)