import datetime
import os
import pipes
import traceback
import time
from contextlib import contextmanager

import pymysql
from dotenv import load_dotenv

from core import errors
from core.utils import docker_command, stringify_given_datetime_or_current_datetime, generate_hashed_password


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
    
    _create_default_users()
    

def _create_default_users():
    
    if not get_user(name='admin'):
        ADMIN_NAME = os.getenv('ADMIN_NAME')
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
        print("Created admin user")
        insert_user(ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD, 0)
    
    if not get_user(name='daehan'):
        SUPER_USER_NAME = os.getenv('SUPER_USER_NAME')
        SUPER_USER_EMAIL = os.getenv('SUPER_USER_EMAIL')
        SUPER_USER_PASSWORD = os.getenv('SUPER_USER_PASSWORD')
        print("Created super user")
        insert_user(SUPER_USER_NAME, SUPER_USER_EMAIL, SUPER_USER_PASSWORD, 0)


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


def insert_user(user_name, email, password, user_type):
    hashed_password, salt = generate_hashed_password(password)
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = "INSERT into user(name, email, password, salt, user_type) values (%s,%s,%s,%s,%s)"
            cur.execute(sql, (user_name, email, hashed_password, salt, user_type))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def get_user_hashed_password_with_user_id(name):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, password, salt
                FROM user
            """
            sql = add_condition_to_query(sql, "name", name)
            cur.execute(sql)
            conn.commit()
            res = cur.fetchone()
            return res
    except:
        traceback.print_exc()
        return False


def get_users():
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, name, email, user_type, login_counting, create_datetime, update_datetime
                FROM user
            """
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
            return res
    except:
        traceback.print_exc()
        return False


def get_user(id_=None, name=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT id, name, email, user_type, login_counting, create_datetime, update_datetime
                FROM user
            """
            if id_ is not None:
                sql = add_condition_to_query(sql, "id", id_)
            elif name is not None:
                sql = add_condition_to_query(sql, "name", name)
        
            cur.execute(sql)
            conn.commit()
            res = cur.fetchone()

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
                WHERE id in ({','.join(str(user_id) for user_id in user_ids)})
            """
            cur.execute(sql)
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def insert_task_group(user_id, title, text, repeat_type, selected_date=None, end_date=None):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into task_group(title, text, user_id, repeat_type, selected_date, end_date) values (%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (title, text, user_id, repeat_type, selected_date, end_date))
            conn.commit()
            return cur.lastrowid
    except:
        traceback.print_exc()
        return False

def insert_task(group_id, datetimes):
    task_datimes = []
    for datetime_ in datetimes:
        datetime_ = stringify_given_datetime_or_current_datetime(datetime_)
        task_datimes.append((group_id, datetime_))
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into task(group_id, datetime) values (%s,%s)"
            cur.executemany(sql, task_datimes)
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False

def verify_task_owner(user_id, task_id):
    return get_tasks(id_=task_id, user_id=user_id)
    

def update_task(task_id, checked=None, datetime_=None):
    if checked is None and datetime_ is None:
        return None
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = "UPDATE task SET "
            if checked is not None:
                sql += f"checked={checked}, "
            if datetime_ is not None:
                datetime_ = datetime.datetime.strptime(datetime_, '%Y-%m-%dT%H:%M')
                sql += f"datetime='{datetime_}', "
            sql = sql[:-2] # remove ', ' at the end
            sql += f" WHERE id={task_id}"
            
            cur.execute(sql)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return False

def get_task_groups(id_=None, user_id=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT
                    *
                FROM
                    task_group as tg
            """
            if id_ is not None:
                sql = add_condition_to_query(sql, "id", id_)
                cur.execute(sql)
                conn.commit()
                res = cur.fetchone()
            else:
                if user_id is not None:
                    sql = add_condition_to_query(sql, "user_id", user_id)
                cur.execute(sql)
                conn.commit()
                res = cur.fetchall()

        return res
    except:
        traceback.print_exc()
        return False


def delete_tasks(ids):
    """
    :param ids: a list of task ids
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                DELETE FROM task
                WHERE id in ({','.join(str(id_) for id_ in ids)})
            """
            cur.execute(sql)
            conn.commit()
    except:
        traceback.print_exc()


def delete_task_groups(ids):
    """
    :param ids: a list of task ids
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                DELETE FROM task_group
                WHERE id in ({','.join(str(id_) for id_ in ids)})
            """
            cur.execute(sql)
            conn.commit()
    except:
        traceback.print_exc()


def get_tasks(id_=None, user_id=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT
                    t.*, tg.title, tg.text, tg.user_id
                FROM
                    task as t
                JOIN 
                    task_group as tg
                ON 
                    t.group_id = tg.id
            """
            if id_ is not None:
                sql = add_condition_to_query(sql, "t.id", id_)
                
                if user_id is not None:
                    sql = add_condition_to_query(sql, "tg.user_id", user_id, is_first_condition=False)
                cur.execute(sql)
                conn.commit()
                res = cur.fetchone()
                
            else:
                if user_id is not None:
                    sql = add_condition_to_query(sql, "tg.user_id", user_id)
                cur.execute(sql)
                conn.commit()
                res = cur.fetchall()

        return res
    except:
        traceback.print_exc()
        return False

def get_task_groups_links(task_groupd_id):
    # TODO: check user id of link
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT
                    lk.*
                FROM
                    task_group_link as tglk
                JOIN 
                    link as lk
                ON
                    tglk.link_id = lk.id
            """
            sql = add_condition_to_query(sql, "tglk.task_group_id", task_groupd_id)
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()

        return res
    except:
        traceback.print_exc()
        return False
    

def insert_link(user_id, url,description, image_url):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into link(url, description, image_url, user_id) values (%s,%s,%s, %s)"
            cur.execute(sql, (url, description, image_url, user_id))
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def get_links(id_=None):
    try:
        with get_db() as conn:

            cur = conn.cursor()
            sql = """
                SELECT
                    *
                FROM link
            """
            if id_ is None:
                cur.execute(sql)
                conn.commit()
                res = cur.fetchall()
                
            else:
                sql = add_condition_to_query(sql, "id", id_)
                cur.execute(sql)
                conn.commit()
                res = cur.fetchone()

        return res
    except:
        traceback.print_exc()


def delete_links(ids):
    """
    :param ids: a list of link ids
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = f"""
                DELETE FROM link
                WHERE id in ({','.join(str(id_) for id_ in ids)})
            """
            cur.execute(sql)
            conn.commit()
    except:
        traceback.print_exc()


def insert_task_group_link(task_group_id_with_link_list):

    try:
        with get_db() as conn:
            cur = conn.cursor()
            sql = "INSERT into task_group_link(task_group_id, link_id) values (%s,%s)"
            cur.executemany(sql, task_group_id_with_link_list)
            conn.commit()

        return True
    except:
        traceback.print_exc()
        return False


def add_condition_to_query(sql, col, row, is_first_condition=True):
    if is_first_condition:
        sql += " WHERE "
    else:
        sql += " AND "
    if isinstance(row, int):
        sql += f" {col}={row}"
    elif isinstance(row, str):
        sql += f" {col}='{row}'"
    return sql

def add_multiple_conditions_to_query(sql, cols_rows):
    sql += " WHERE"
    for col_row in cols_rows:
        col = col_row["col"]
        row = col_row["row"]
        if isinstance(col_row["col"], int):
            sql += f" {col}={row}"
        else:
            sql += f" {col}='{row}'"
