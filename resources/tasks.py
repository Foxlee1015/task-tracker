# -*- coding: utf-8 -*-
import datetime
import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response, json_serializer, json_serializer_all_datetime_keys
from core.utils import check_if_only_int_numbers_exist, token_required

api = Namespace('tasks', description='Tasks related operations')


def _create_task(user_id, title, text, repeat_type, link_ids, start_date, end_date):
    """Create a task group annd tasks based on the task group 
    
    NOTE: 
        First, create a new task group and then create tasks 
        depends on repeat time, start date and end date
    """
    try:
        task_dates = create_task_dates_by_repeat_type(repeat_type, 
                                                    start_date, end_date)
        task_group_id = db.insert_task_group(user_id, title, text, repeat_type, selected_date=task_dates[0], end_date=task_dates[-1])
        
        db.insert_task(task_group_id, task_dates)
        
        if link_ids is not None:
            task_group_id_with_link_list = []
            for link_id in link_ids:
                task_group_id_with_link_list.append((task_group_id, link_id))
            db.insert_task_group_link(task_group_id_with_link_list)

        return True
    except:
        traceback.print_exc()
        return False

def create_task_dates_by_repeat_type(repeat_type, start_date, end_date):
    """
     
    :param repeat_type: 0 - no repeat, 1 - weekly, 2 - monthly, 3 - yearly, 4 - Biweekly
    """
    print(start_date, end_date)
    if start_date is None:
        start_date = datetime.datetime.now()
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M')

    task_dates = [start_date]
    if repeat_type == 0:
        return task_dates

    if end_date is None:
        if repeat_type == 3:
            end_date = start_date + datetime.timedelta(years=365*5)
        else:
            end_date = start_date + datetime.timedelta(days=180)
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

    task_date = start_date
    while task_date <= end_date:
        if repeat_type == 1:
            task_date = task_date + datetime.timedelta(days=7)
        elif repeat_type == 2:
            task_date = task_date + datetime.timedelta(days=30)
        elif repeat_type == 3:
            task_date = task_date + datetime.timedelta(days=365)
        elif repeat_type == 4:
            task_date = task_date + datetime.timedelta(days=14)

        task_dates.append(task_date)
    return task_dates
        


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
parser_delete.add_argument('Authorization', type=str, required=True, location='headers')



@api.route('/groups')
class TaskGoup(CustomResource):
    @api.doc('get all tasks')
    def get(self):
        task_groups = db.get_task_groups()
        
        # sort by task datetime
        for task_group in task_groups:
            task_group = json_serializer_all_datetime_keys(task_group)
        
        return self.send(status=200, result=task_groups)
    
    @api.doc('create a new task')
    @api.expect(parser_create)
    def post(self):
        args = parser_create.parse_args()
        title = args["title"]
        text = args["text"]        
        repeat_type = args["repeat_type"]
        link_ids = args.get("link_ids")
        start_date = args.get("selected_date")
        end_date = args.get("end_date")

        result = _create_task(2, title, text, repeat_type, link_ids, 
                                start_date, end_date)
        status = 201 if result else 400
        return self.send(status=status)

    @api.doc('delete task group')
    @api.expect(parser_delete)
    @token_required
    def delete(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        args = parser_delete.parse_args()
        ids = args["ids"]
        if check_if_only_int_numbers_exist(ids):
            result = db.delete_task_groups(args['ids'])
            return self.send(status=200)
        else:
            return self.send(status=400, message="Check user ids")


@api.route('/group/<int:id_>')
@api.param('id_', 'The task identifier')
@api.response(404, 'Task not found')
class Task(CustomResource):
    @api.doc('get_tasks')
    def get(self, id_):
        '''Fetch a task group given its identifier'''
        task_group = db.get_task_groups(id_=id_)
        if task_group:
            task_group = json_serializer_all_datetime_keys(task_group)
            task_group["links"] = db.get_task_groups_links(id_)
            return self.send(status=200, result=task_group)
        else:
            return self.send(status=404, result=None)

    @api.doc('delete a task')
    def delete(self, id_):
        '''Fetch a session given its identifier'''
        db.delete_tasks(ids=[id_])
        return self.send(status=200)


@api.route('/')
class Tasks(CustomResource):
    @api.doc('get all tasks')
    def get(self):
        tasks = db.get_tasks()
        
        # sort by task datetime
        for task in tasks:
            task['datetime'] = json_serializer(task['datetime'])
        
        if tasks:
            return self.send(status=200, result=tasks)
        else:
            return self.send(status=203, result=None)

    @api.doc('delete tasks')
    @api.expect(parser_delete)
    def delete(self):
        args = parser_delete.parse_args()
        ids = args["ids"]
        if check_if_only_int_numbers_exist(ids):
            result = db.delete_tasks(ids=ids)
            return self.send(status=200)
        else:
            return self.send(status=400, message="Check user ids")



@api.route('/<int:id_>')
@api.param('id_', 'The task identifier')
@api.response(404, 'Task not found')
class Task(CustomResource):
    @api.doc('get_tasks')
    def get(self, id_):
        '''Fetch an task given its identifier'''
        task = db.get_tasks(id_=id_)
        if task is None:
            return self.send(status=404, result=None) 
        task = json_serializer_all_datetime_keys(task)
        return self.send(status=200, result=task)
        
        
    @api.doc('delete a task')
    def delete(self, id_):
        '''Fetch a session given its identifier'''
        result = delete_tasks([id_])
        return self.send(status=200)
