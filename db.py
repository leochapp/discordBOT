import datetime
import os
import pymysql as MySQLdb
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = os.environ['HOST']
username = os.environ['USER']
password = os.environ['PASSWORD']
db2 = os.environ['DATABASE']


def get_server_info():
    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    query = "SELECT uid FROM servers"
    cursor.execute(query)
    tab_sever_info = cursor.fetchall()
    query = "SELECT * FROM members";
    cursor.execute(query)
    tab_users_info = cursor.fetchall()
    conn.close()
    return tab_sever_info, tab_users_info

def add_server(server):
    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    query = "INSERT INTO servers VALUES(%s, %s)"
    cursor.execute(query, server)
    conn.commit()
    conn.close()

def add_user(user, name):
    my_datetime = datetime.datetime.now()
    current_datetime = my_datetime.strftime('%Y-%m-%d %H:%M:%S')

    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    try:
        query1 = "INSERT INTO users VALUES (%s,%s)"
        cursor.execute(query1, (user[0], name))
    except:
        pass
    query2 = "INSERT INTO members VALUES (%s,%s, %s)"
    cursor.execute(query2, (user[0], user[1], current_datetime))
    conn.commit()
    conn.close()

def update_users_info():
    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    query = "SELECT user_id,server_id FROM members";
    cursor.execute(query)
    tab_users_info = cursor.fetchall()
    conn.close()
    return tab_users_info

def update_server_info():
    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    query = "SELECT uid FROM servers"
    cursor.execute(query)
    tab_sever_info = cursor.fetchall()
    conn.close()
    return tab_sever_info

def add_music_palyed(url, userid, server):
    my_datetime = datetime.datetime.now()
    current_datetime = my_datetime.strftime('%Y-%m-%d %H:%M:%S')

    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    values = (None, url, userid, server, current_datetime)
    query = "INSERT INTO datamusic VALUES(%s,%s,%s,%s,%s)"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def verifyrole(role, user_id, server_id):
    parameters = (server_id, role, user_id)
    if role == "admin":
        query = f"SELECT COUNT(*) FROM tools WHERE server_id = %s AND isadmin = %s AND user_id = %s"
    else:
        query = f"SELECT COUNT(*) FROM tools WHERE server_id = %s AND istarget = %s AND user_id = %s"
    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()
    cursor.execute(query, parameters)
    result = cursor.fetchone()[0]
    db.close()
    if result == 1:
        return True
    else:
        return False

def get_last_url(server_id):
    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()
    parameters = (server_id,)
    query = "SELECT url FROM datamusic WHERE server_id=%s ORDER BY date_time DESC LIMIT 1;"
    cursor.execute(query, parameters)
    url = cursor.fetchone()[0]
    return url
