import os
import pymysql as MySQLdb
from dotenv import load_dotenv, find_dotenv
import datetime



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

def add_user(member):
    my_datetime = datetime.datetime.now()
    current_datetime = my_datetime.strftime('%Y-%m-%d %H:%M:%S')

    conn = MySQLdb.connect(host=host, database=db2, user=username, password=password)
    cursor = conn.cursor()
    try:
        query1 = "INSERT INTO users VALUES (%s,%s)"
        cursor.execute(query1, (member.id, member.name))
    except:
        print("utilisateur déjà ajouté")
    query2 = "INSERT INTO members VALUES (%s,%s, %s)"
    cursor.execute(query2, (member.id, member.server.id, current_datetime))
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

def getdata(role,serv):

    if role =="admin":
        role = "isadmin"
    else:
        role = "istarget"

    db = MySQLdb.connect(host=host, user=username, password=password, database=db2)
    cursor = db.cursor()
    parameters = (serv, role)
    query = f"SELECT user_id FROM tools WHERE server_id = %s AND {role} = 1"
    cursor.execute(query, parameters)
    tab = cursor.fetchall()
    data = []
    for tup in tab:
        data.append(tup[0])
    db.close()
    print(data)
    return data