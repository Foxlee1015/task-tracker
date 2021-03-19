from datetime import datetime
import jwt
import os
import paramiko
import traceback
import string
import random
import hashlib

from flask import request, current_app
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

host = os.getenv('SSH_HOST')
port = int(os.getenv('SSH_PORT'))
usr = os.getenv('SSH_USER')
pwd = os.getenv('SSH_PASSWORD')


def token_required(f):
    def wrapper(*args, **kwargs):
        # print(request.headers)
        auth_header = request.headers.get('Authorization')
        current_user = 1
        print(auth_header)
        if auth_header:
            try:
                access_token = auth_header.split(' ')[1]
                try:
                    token = jwt.decode(access_token, current_app.config['SECRET_KEY'])
                    print("token : " , token)
                # except jwt.ExpiredSignatureError as e:
                #     raise e
                # except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                #     raise e
                except:
                    return False #api.abort(401, 'Unknown token error')

            except IndexError:
                raise jwt.InvalidTokenError
        else:
            return False # api.abort(403, 'Token required')
        return f(*args, **kwargs, current_user=current_user)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper

def execute_command_ssh(cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port, usr, pwd)
    except paramiko.ssh_exception.SSHException: # tcp timeout
        traceback.print_exc()
        return None, None

    _, stdout, stderr = client.exec_command(cmd)
    result_stdout, result_stderr = stdout.read(), stderr.read()
    client.close()

    if result_stdout is None:
        return None
    else:
        result_stdout = result_stdout.decode('utf-8')
    if result_stderr is not None:
        result_stderr = result_stderr.decode('utf-8')

    return result_stdout, result_stderr

def docker_command(container_name, cmd):
    try:
        execute_command_ssh(f'docker exec -i {container_name} /bin/sh -c "{cmd}"')
    except Exception as e:
        traceback.print_exc()
        print(e)

def stringify_given_datetime_or_current_datetime(datetime_=None, format_='%Y-%m-%d %H:%M:%S'):
    '''
    :param format_: '%Y-%m-%d %H:%M:%S' is for database
    '''
    try:
        if datetime_ is None:
            datetime_ = datetime.now()
        return datetime_.strftime(format_)
    except Exception as e:
        traceback.print_exc()
        print(e)

def check_if_only_int_numbers_exist(numbers):
    for number in numbers:
        try:
            number = int(number)
        except:
            return False
    return True

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))

def generate_hashed_password(password):
    random_salt =  random_string(random.randint(4, 10))
    password_with_salt = password + random_salt
    hashed_password = hashlib.sha512(password_with_salt.encode('utf-8')).hexdigest()
    return hashed_password, random_salt

def verify_password(password, salt, hashed_password):
    password_with_salt = password + salt
    if hashed_password == hashlib.sha512(password_with_salt.encode('utf-8')).hexdigest():
        return True
    else:
        False