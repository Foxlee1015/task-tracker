from datetime import datetime
import os
import paramiko
import traceback

from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

host = os.getenv('SSH_HOST')
port = int(os.getenv('SSH_PORT'))
usr = os.getenv('SSH_USER')
pwd = os.getenv('SSH_PASSWORD')


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