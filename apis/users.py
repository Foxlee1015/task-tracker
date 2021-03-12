from flask_restplus import Namespace, Resource, fields

from core.db import insert_user, get_users, delete_users, backup_db
from core.resource import CustomResource, response, json_serial
from core.utils import execute_command_ssh


api = Namespace('users', description='Users related operations')


@api.route('/')
class Users(CustomResource):
    @api.doc('list_users')
    def get(self):
        print('test')
        '''List all users'''        
        users = get_users()
        for user in users:
            user['create_datetime'] = json_serial(user['create_datetime'])

        res = response(status = 1, result = {"users":users})
        return self.send(res)


    @api.doc('create a new user')
    def post(self):
        '''Create an user'''
        result = insert_user("1", "b", 2)
        print(result)
        return "ok"


    @api.doc('delete_users')
    def delete(self):
        '''Delete all users'''
        result = delete_users([1,2,3])
        print(result)
        return "ok"


@api.route('/<id>')
@api.param('id', 'The user identifier')
@api.response(404, 'User not found')
class User(CustomResource):
    @api.doc('get_user')
    def get(self, id):
        '''Fetch a user given its identifier'''
        for user in users:
            if user['id'] == id:
                return user
        api.abort(404)
