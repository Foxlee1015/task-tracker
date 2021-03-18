import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core.db import insert_user, get_user, get_users, delete_users, backup_db
from core.resource import CustomResource, response, json_serializer_all_datetime_keys
from core.utils import execute_command_ssh


api = Namespace('users', description='Users related operations')

parser_create = reqparse.RequestParser()
parser_create.add_argument('name', type=str, required=True, location='form', help='Unique user name')
parser_create.add_argument('email', type=str, location='form')
parser_create.add_argument('password', type=str, required=True, location='form', help='Password')
parser_create.add_argument('password_confirm', type=str, required=True, location='form', help='Confirm password')

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('ids', type=str, required=True, action='split')


def _get_users():
    try:
        users = get_users()
        for user in users:
            user = json_serializer_all_datetime_keys(user)
        return users
    except:
        traceback.print_exc()
        return None
        

def _create_user(name, email, password, user_type=2):
    try:
        result = insert_user(name, email, password, user_type)
        return result
    except:
        traceback.print_exc()
        return None
        

@api.route('/')
class Users(CustomResource):
    @api.doc('list_users')
    def get(self):
        '''List all users
        
        NOTE: Only for admin users
        '''        
        users = _get_users()
        if users is None:
            res = response(status=203)
        else:
            res = response(status=200, result=users)
        return self.send(res)


    @api.doc('create a new user')
    @api.expect(parser_create)
    def post(self):
        '''Create an user'''
        args = parser_create.parse_args()
        name = args["name"]
        email = args["email"]
        password = args["password"]
        password_confirm = args["password_confirm"]
        
        if password_confirm != password:
            return self.send(response(status=400))
        if get_user(name=name):
            return self.send(response(status=409, message="The given username alreay exists."))
        
        result = _create_user(name, email, password)
        status = 201 if result else 500
        return self.send(response(status=status))


    @api.doc('delete_users')
    @api.expect(parser_delete)
    def delete(self):
        '''Delete all users
        
        NOTE: Only for admin users or user owner
        '''
        args = parser_delete.parse_args()
        result = delete_users(args['ids'])
        return self.send(response(status=200))


@api.route('/<id_>')
@api.param('id_', 'The user identifier')
@api.response(404, 'User not found')
class User(CustomResource):
    @api.doc('get_user')
    def get(self, id_):
        '''Fetch a user given its identifier'''
           
        user = get_user(id_=id_)
        if user is None:
            return self.send(response(status=404, result=None)) 
        user = json_serializer_all_datetime_keys(user)
        return self.send(response(status=200, result=user))
        
    
    @api.doc('delete_user')
    def delete(self, id_):
        '''Delete an user'''
        result = delete_users([id_])
        return self.send(response(status=200))
