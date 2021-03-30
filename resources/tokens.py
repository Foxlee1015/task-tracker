import jwt
import traceback
import datetime
from flask import current_app
from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response
from core.utils import token_required
from .users import return_user_id_if_user_password_is_correct

api = Namespace('tokens', description='Sessions related operations')


JWT_EXPIRATION_HOURS = 8

def create_jwt(user_id, username):
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
        "uid": user_id,
        "iss": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.utcnow(),
        "is_admin": is_admin
    }
    encoded_jwt = jwt.encode(
                            token_payload, current_app.config["SECRET_KEY"], 
                            algorithm=token_header["alg"], headers=token_header)
    return encoded_jwt


def get_user_info_if_token_is_valid(token):
    try:
        access_token = token.split(' ')[1]
        try:
            user_info = jwt.decode(access_token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            return user_info, ""
        except jwt.ExpiredSignatureError:
            return None, "Token has been expired error"
        except jwt.exceptions.DecodeError as e:
             return None, "Token decode error"
    except Exception as e:
         return None, "Token format error"

    
parser_create = reqparse.RequestParser()
parser_create.add_argument('username', type=str, action='form')
parser_create.add_argument('password', type=str, location='form')
parser_create.add_argument('Authorization', type=str, location='headers')


@api.route('/')
class Token(CustomResource):
    @api.doc('create jwt')
    @api.expect(parser_create)
    @token_required
    def post(self, current_user, **kwargs):
        if current_user is not None:
            res = create_jwt(current_user["uid"], current_user["iss"])
            return self.send(status=201, result=res)
        args = parser_create.parse_args()
        username = args.get("username")
        password = args.get("password")

        if not db.get_user(name=username):
            return self.send(status=404)
        
        user_id = return_user_id_if_user_password_is_correct(username, password)
        if user_id:
            res = create_jwt(user_id, username)
            return self.send(status=201, result=res)
        return self.send(status=400)

   
parser_validation = reqparse.RequestParser()
parser_validation.add_argument('Authorization', type=str, required=True, location='headers')

@api.route('/validate')
class TokenValidation(CustomResource):
    @api.doc('validate jwt')
    @api.expect(parser_validation)
    def post(self):
        args = parser_validation.parse_args()
        token = args.get("Authorization")
        
        if token is not None:
            user_info, message_if_not_valid = get_user_info_if_token_is_valid(token)
            if user_info is not None:
                return self.send(status=200, result=user_info)
            else:
                 return self.send(status=400, message=message_if_not_valid)
        return self.send(status=400)