import jwt
import traceback
import datetime
from flask import current_app
from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response
from .users import return_user_id_if_user_password_is_correct

api = Namespace('tokens', description='Sessions related operations')


JWT_EXPIRATION_HOURS = 8

def create_jwt(username):
    """
    NOTE:
        https://pyjwt.readthedocs.io/en/latest/index.html
    """
    is_admin = True if username == "admin" else False
    token_header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    token_payload = {
        "iss": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.utcnow(),
        "is_admin": is_admin
    }
    encoded_jwt = jwt.encode(
                            token_payload, current_app.config["SECRET_KEY"], 
                            algorithm=token_header["alg"], headers=token_header)
    return encoded_jwt

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

        if not db.get_user(name=username):
            return self.send(status=404)
        
        if return_user_id_if_user_password_is_correct(username, password):
            res = create_jwt(username)
            return self.send(status=201, result=res)
        else:
            return self.send(status=400)

