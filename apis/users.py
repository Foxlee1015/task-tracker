from flask_restplus import Namespace, Resource, fields

from core.db import insert_user, get_users, delete_users, backup_db
from core.resource import CustomResource, response, json_serializer_all_datetime_keys
from core.utils import execute_command_ssh


api = Namespace('users', description='Users related operations')


@api.route('/')
class Users(CustomResource):
    @api.doc('list_users')
    def get(self):
        '''List all users'''        
        users = get_users()
        for user in users:
            user = json_serializer_all_datetime_keys(user)

        res = response(status=1, result =users)
        return self.send(res)


    @api.doc('create a new user')
    def post(self):
        '''Create an user'''
        result = insert_user("1", "b", 2)
        res = response(status=1)
        return self.send(res)


    @api.doc('delete_users')
    def delete(self):
        '''Delete all users'''
        result = delete_users([1,2,3])
        print(result)
        return "ok"


@api.route('/<_id>')
@api.param('_id', 'The user identifier')
@api.response(404, 'User not found')
class User(CustomResource):
    @api.doc('get_user')
    def get(self, id_):
        '''Fetch a user given its identifier'''
           
        user = get_user(id_=id_)
        user = json_serializer_all_datetime_keys(user)
        res = response(status=1, result=user)
        return self.send(res)
        