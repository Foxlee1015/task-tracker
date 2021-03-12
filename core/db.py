import datetime
import os
import pipes
import traceback
import time
from contextlib import contextmanager

import pymysql
from dotenv import load_dotenv

from core import errors
from core.utils import docker_command


# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)
    

db_host_dev = os.getenv('DB_HOST_DEV')
db_host = os.getenv('DB_HOST')
db_port = int(os.getenv('DB_PORT'))
db_user = os.getenv('DB_USERNAME')
db_pw = os.getenv('DB_PASSWORD')
db_dataset = os.getenv('DB_DATABASE')
db_charset = os.getenv('DB_CHARSET')

db_info_kwargs = {
    "host": db_host_dev,
    "port": db_port,
    "user": db_user,
    "password": db_pw,
    "db": db_dataset,
    "charset": db_charset,
    "cursorclass": pymysql.cursors.DictCursor
}

@contextmanager
def get_db():
    try:
        conn = None
        try:
            conn = pymysql.connect(**db_info_kwargs)
        except:
            print("db host dev connect exception")
            db_info_kwargs["host"] = db_host
            conn = pymysql.connect(**db_info_kwargs)
        yield conn
    except:
        traceback.print_exc()
    finally:
        conn.close()
        pass


def init_db():
    with get_db() as conn:
        from core import schema
        sql_list= schema.schema.split(";")
        for sql in sql_list:
            if sql != '' and sql != '\n':
                try:
                    conn.cursor().execute(sql)
                except:
                    traceback.print_exc()
        conn.commit()

def backup_db():
    BACKUP_PATH = '/var/backups'
    DATETIME = time.strftime('%Y%m%d_%H%M%S')
    TODAYBACKUPPATH = f"{BACKUP_PATH}/{DATETIME}"
    MYSQL_DB_DICRECTORY = f'/var/lib/mysql/{db_dataset}'
    MYSQL_CONTAINER = 'cook_mysql'

    try:
        mkdir_cmd = f"mkdir {TODAYBACKUPPATH}"
        docker_command(MYSQL_CONTAINER, mkdir_cmd)

        mysql_dump_cmd = f"mysqldump -u {db_user} -p{db_pw} --databases {db_dataset} > {TODAYBACKUPPATH}/{db_dataset}.sql"        
        docker_command(MYSQL_CONTAINER, mysql_dump_cmd)
        
        print("Your backups have been created in '" + TODAYBACKUPPATH + "' directory")
    except Exception as e:
        traceback.print_exc()
        print("db back error : ", e)


def insert_user(user_name, email, user_type):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = "INSERT into user(name, email, user_type) values (%s,%s,%s)"
            cur.execute(sql, (user_name, email, user_type))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def get_users():
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT *
                FROM user
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()

        return res
    except:
        traceback.print_exc()
        return False
    

def delete_users(user_ids):
    """
    :param user_ids: a list of user ids
    """
    try:
        with get_db() as conn:

            cur = conn.cursor()

            sql = f"""
                DELETE FROM user
                WHERE id in ({','.join(str(user_Id) for user_id in user_ids)})
            """
            cur.execute(sql)
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False
