import json
from sqlalchemy import create_engine  # 连接数据库的方法
from sqlalchemy.orm import sessionmaker
import pymysql

def connect_db(host,port,db,user,pwd):
    # 连接数据库
    HOSTNAME = host
    DATABASE = db
    USERNAME = user
    PASSWORD = pwd
    #Db_Uri = 'mysql+mysqlconnector://{}:{}@{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME,
    #                                                                  DATABASE)  # 连接数据库的uri# mysql+pymysql://{用户名}:{密码}@{host}:{port}/{数据库}?charset=utf8
    db = pymysql.connect(host=HOSTNAME, port=port, user=USERNAME, passwd=PASSWORD, db=DATABASE, charset='utf8')
    cursor = db.cursor()
    #engine = create_engine(Db_Uri)  # 连接数据库
    # 创建会话
    #Session = sessionmaker(bind=engine)
    #session = Session()
    print("数据库创建成功")
    return cursor


















