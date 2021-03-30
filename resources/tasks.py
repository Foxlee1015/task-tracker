# -*- coding: utf-8 -*-
import datetime
import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response, json_serializer, json_serializer_all_datetime_keys
from core.utils import check_if_only_int_numbers_exist, token_required, parse_given_str_datetime_or_current_datetime

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
        
        task_group_id_with_link_list = []
        for link_id in link_ids:
            if link_id != "":
                task_group_id_with_link_list.append((task_group_id, link_id))
        if task_group_id_with_link_list:
            db.insert_task_group_link(task_group_id_with_link_list)

        return True
    except:
        traceback.print_exc()
        return False

def create_task_dates_by_repeat_type(repeat_type, start_date, end_date):
    """
     
    :param repeat_type: 0 - No repeat, 1 - Weekly, 2 - Monthly, 3 - Yearly, 4 - Biweekly, 5 - Everyday
    """
    if start_date is None:
        start_date = datetime.datetime.now()
    else:
        start_date = parse_given_str_datetime_or_current_datetime(start_date)

    task_dates = [start_date]
    if repeat_type == 0:
        return task_dates

    if end_date is None:
        if repeat_type == 3:
            end_date = start_date + datetime.timedelta(years=365*5)
        else:
            end_date = start_date + datetime.timedelta(days=180)
    else:
        end_date = parse_given_str_datetime_or_current_datetime(end_date)

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
        elif repeat_type == 5:
            task_date = task_date + datetime.timedelta(days=1)

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

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, required=True, location='headers')


@api.route('/groups')
class TaskGoup(CustomResource):
    @api.doc('get all tasks')
    @api.expect(parser_header)
    @token_required
    def get(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])

        task_groups = db.get_task_groups(user_id=current_user["uid"])
        if not task_groups:
            return self.send(status=203, result=None)

        task_groups = sorted(task_groups, key=lambda x: x['datetime'])
        for task_group in task_groups:
            task_group = json_serializer_all_datetime_keys(task_group)
        
        return self.send(status=200, result=task_groups)
    
    @api.doc('create a new task')
    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        args = parser_create.parse_args()
        title = args["title"]
        text = args["text"]        
        repeat_type = args["repeat_type"]
        link_ids = args.get("link_ids")
        start_date = args.get("selected_date")
        end_date = args.get("end_date")

        result = _create_task(current_user["uid"], title, text, repeat_type, link_ids, 
                                start_date, end_date)
        status = 201 if result else 400
        return self.send(status=status)

    @api.doc('delete task group')
    @api.expect(parser_delete, parser_header)
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
    @api.expect(parser_header, parser_header)
    @token_required
    def get(self, id_, current_user, **kwargs):
        '''Fetch a task group given its identifier'''
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        task_group = db.get_task_groups(id_=id_)
        if task_group:
            task_group = json_serializer_all_datetime_keys(task_group)
            task_group["links"] = db.get_task_groups_links(id_)
            return self.send(status=200, result=task_group)
        else:
            return self.send(status=404, result=None)

    @api.doc('delete a task')
    @api.expect(parser_header)
    @token_required
    def delete(self, id_, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        '''Fetch a session given its identifier'''
        db.delete_tasks(ids=[id_])
        return self.send(status=200)


@api.route('/')
class Tasks(CustomResource):
    @api.doc('get all tasks')
    @api.expect(parser_header)
    @token_required
    def get(self, current_user, **kwargs):
        try:
            if current_user is None:
                return self.send(status=400, message=kwargs["error_msg"])
            tasks = db.get_tasks(user_id=current_user["uid"])
            if not tasks:
                return self.send(status=203, result=None)

            tasks = sorted(tasks, key=lambda x: x['datetime']) #, reverse=True)
            for task in tasks:
                task['datetime'] = json_serializer(task['datetime'])
            
            return self.send(status=200, result=tasks)
        except:
            traceback.print_exc()
            return self.send(status=500, result=None)
        

    @api.doc('delete tasks')
    @api.expect(parser_delete)
    @api.expect(parser_header)
    @token_required
    def delete(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        args = parser_delete.parse_args()
        ids = args["ids"]
        if check_if_only_int_numbers_exist(ids):
            result = db.delete_tasks(ids=ids)
            return self.send(status=200)
        else:
            return self.send(status=400, message="Check user ids")


parser_update_task = reqparse.RequestParser()
parser_update_task.add_argument('checked', type=int, location='args', help='check when tasks are finished')
parser_update_task.add_argument('task_datetime', type=str, location='args', help='check when tasks are finished')


@api.route('/<int:id_>')
@api.param('id_', 'The task identifier')
@api.response(404, 'Task not found')
class Task(CustomResource):
    @api.doc('get_tasks')
    @api.expect(parser_header)
    @token_required
    def get(self, id_, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        '''Fetch an task given its identifier'''
        task = db.get_tasks(id_=id_, user_id=current_user["uid"])
        if task is None:
            return self.send(status=404, result=None) 
        task = json_serializer_all_datetime_keys(task)
        return self.send(status=200, result=task)
    
    @api.doc('update a task')
    @api.expect(parser_header, parser_update_task)
    @token_required
    def post(self, id_, current_user, **kwargs):
        try:
            if current_user is None:
                return self.send(status=400, message=kwargs["error_msg"])
            args = parser_update_task.parse_args()
            checked = args.get("checked")
            task_datetime = args.get("task_datetime")
            if db.verify_task_owner(current_user["uid"], id_):
                task = db.update_task(id_, checked=checked, datetime_=task_datetime)
                if task:
                    return self.send(status=200) 
            else:
                return self.send(status=403)
        except:
            traceback.print_exc()
            return self.send(status=400)
        
        
    @api.doc('delete a task')
    @api.expect(parser_header)
    @token_required
    def delete(self, id_, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        result = delete_tasks([id_])
        return self.send(status=200)
