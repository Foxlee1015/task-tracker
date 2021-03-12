from flask_restplus import Namespace, Resource, fields, reqparse

from core import db

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

# https://flask-restplus.readthedocs.io/en/stable/parsing.html
parser_create = reqparse.RequestParser()
parser_create.add_argument('title', type=str, required=True, location='form', help='Title')
parser_create.add_argument('text', type=str, required=True, location='form')

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('ids', type=str, required=True, action='split')

@api.route('/')
class Tasks(Resource):
    @api.doc('get all tasks')
    def get(self):
        return tasks
    
    @api.doc('create a new task')
    @api.expect(parser_create)
    def post(self):
        args = parser_create.parse_args()
        title = args["title"]
        text = args["text"]
        db.insert_task(1, title, text)
        return tasks

    @api.doc('delete tasks')
    @api.expect(parser_delete)
    def delete(self):
        args = parser_delete.parse_args()
        print(args)
        return tasks


@api.route('/<id>')
@api.param('id', 'The task identifier')
@api.response(404, 'Task not found')
class Task(Resource):
    @api.doc('get_tasks')
    def get(self, id):
        '''Fetch an task given its identifier'''
        for task in tasks:
            if task['id'] == id:
                return task
        api.abort(404)
    
    @api.doc('delete a task')
    def delete(self, id):
        '''Fetch a session given its identifier'''
        if id == 1:
            return id
        else:
            api.abort(404)