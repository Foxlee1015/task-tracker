# -*- coding: utf-8 -*-
import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response, json_serial

api = Namespace('tasks', description='Tasks related operations')


def create_task(user_id, title, text, repeat_type, link_ids):
    try:
        row_id = db.insert_task_group(user_id, title, text, repeat_type)
        db.insert_task(row_id) # need to add task time
        
        if link_ids is not None:
            task_group_id_with_link_list = []
            for link_id in link_ids:
                task_group_id_with_link_list.append((row_id, link_id))
            db.insert_task_group_link(task_group_id_with_link_list)

        return True
    except:
        traceback.print_exc()
        return False


# https://flask-restplus.readthedocs.io/en/stable/parsing.html
parser_create = reqparse.RequestParser()
parser_create.add_argument('title', type=str, required=True, location='form', help='Title')
parser_create.add_argument('text', type=str, required=True, location='form')
parser_create.add_argument('selected_date', type=str, location='form', help='its for monthly or yearly events. Only future date can be selected')
parser_create.add_argument('repeat_type', type=int, required=True, location='form', help='0 - no repeat, 1 - weekly, 2 - monthly, 3 - yearly, 4 - Biweekly')
parser_create.add_argument('end_date', type=str, location='form', help='when repeating, set up end date. Default value is 6 months after selected date')
parser_create.add_argument('link_ids', type=str, location='form', action='split')

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('ids', type=str, required=True, action='split')

@api.route('/group')
class TaskGoup(CustomResource):
    @api.doc('get all tasks')
    def get(self):
        tasks = db.get_tasks()
        
        # sort by task datetime
        for task in tasks:
            task['datetime'] = json_serial(task['datetime'])
        
        res = response(status=1, result=tasks)
        return self.send(res)
    
    @api.doc('create a new task')
    @api.expect(parser_create)
    def post(self):
        args = parser_create.parse_args()
        title = args["title"]
        text = args["text"]        
        repeat_type = args["repeat_type"]
        link_ids = args.get("link_ids")
        
        result = create_task(1, title, text, repeat_type, link_ids)
        status = 1 if result else 0

        res = response(status=status)
        return self.send(res)

    @api.doc('delete tasks')
    @api.expect(parser_delete)
    def delete(self):
        args = parser_delete.parse_args()
        print(args)
        res = response(status=1)
        return self.send(res)


@api.route('/group/<id_>')
@api.param('id_', 'The task identifier')
@api.response(404, 'Task not found')
class Task(CustomResource):
    @api.doc('get_tasks')
    def get(self, id_):
        '''Fetch an task given its identifier'''
        for task in tasks:
            if task['id'] == id_:
                res = response(status=1, result={task})
                return self.send(res)
        api.abort(404)
    
    @api.doc('delete a task')
    def delete(self, id_):
        '''Fetch a session given its identifier'''
        if id == 1:
            return id
        else:
            api.abort(404)


@api.route('/')
class Tasks(CustomResource):
    @api.doc('get all tasks')
    def get(self):
        tasks = db.get_tasks()
        
        # sort by task datetime
        for task in tasks:
            task['datetime'] = json_serial(task['datetime'])
        
        res = response(status=1, result={tasks})
        return self.send(res)
    
    @api.doc('create a new task')
    @api.expect(parser_create)
    def post(self):
        args = parser_create.parse_args()
        title = args["title"]
        text = args["text"]        
        repeat_type = args["repeat_type"]
        link_ids = args.get("link_ids")
        
        result = create_task(1, title, text, repeat_type, link_ids)
        status = 1 if result else 0

        res = response(status=status)
        return self.send(res)

    @api.doc('delete tasks')
    @api.expect(parser_delete)
    def delete(self):
        args = parser_delete.parse_args()
        print(args)
        res = response(status=1)
        return self.send(res)


@api.route('/<id_>')
@api.param('id_', 'The task identifier')
@api.response(404, 'Task not found')
class Task(CustomResource):
    @api.doc('get_tasks')
    def get(self, id_):
        '''Fetch an task given its identifier'''
        for task in tasks:
            if task['id'] == id_:
                res = response(status=1, result={task})
                return self.send(res)
        api.abort(404)
    
    @api.doc('delete a task')
    def delete(self, id_):
        '''Fetch a session given its identifier'''
        if id == 1:
            return id
        else:
            api.abort(404)