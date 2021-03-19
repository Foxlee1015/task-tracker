from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response, json_serializer
from .users import return_user_id_if_user_password_is_correct

api = Namespace('tokens', description='Sessions related operations')


JWT_EXPIRATION_DAY = 3600 * 24 * 7

def create_jwt(user_id, username):
    json_web_token = 'a'
    return json_web_token

def validate_jwt(jwt):
    return True

def refresh_jwt(user_id):
    # get from db
    token = 'b'
    return x


    
parser_create = reqparse.RequestParser()
parser_create.add_argument('username', type=str, required=True, action='form')
parser_create.add_argument('password', type=str, required=True, location='form')


@api.route('/')
class Token(CustomResource):
    @api.doc('create jwt')
    @api.expect(parser_create)
    def post(self):
        args = parser_create.parse_args()
        username = args["username"]
        password = args["password"]

        user_id = return_user_id_if_user_password_is_correct(username, password)
        if user_id:
            res = create_jwt(user_id, username)
            return self.send(status=201, result=res)
        else:
            return self.send(status=400)

