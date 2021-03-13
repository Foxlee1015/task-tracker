from flask_restplus import Api

from .tasks import api as tasks
from .links import api as links
from .logs import api as logs
from .sessions import api as sessions
from .users import api as users

api = Api(
    title='My Title',
    version='1.0',
    description='A description',
)

api.add_namespace(tasks)
api.add_namespace(links)
api.add_namespace(logs)
api.add_namespace(sessions)
api.add_namespace(users)