from flask_restplus import Namespace, Resource, fields

api = Namespace('tasks', description='Tasks related operations')

tasks = [
    {
        "id": 1,
        "name": 'water'
    },
    {
        "id": 2,
        "name": 'coke'
    }
]

@api.route('/')
class Tasks(Resource):
    @api.doc('list_tasks')
    def get(self):
        '''List all tasks'''
        return tasks

@api.route('/<id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
class Article(Resource):
    @api.doc('get_tasks')
    def get(self, id):
        '''Fetch an task given its identifier'''
        for task in tasks:
            if task['id'] == id:
                return task
        api.abort(404)