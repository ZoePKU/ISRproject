# -*- coding: utf-8 -*

from sqlalchemy import create_engine  # 连接数据库的方法
from sqlalchemy.orm import sessionmaker, scoped_session


def connect_db(host, db, user, pwd):
    # 连接数据库
    HOSTNAME = host
    DATABASE = db
    USERNAME = user
    PASSWORD = pwd
    Db_Uri = 'mysql+mysqlconnector://{}:{}@{}/{}?charset=utf8'.format(USERNAME,
                                                                      PASSWORD,
                                                                      HOSTNAME,
                                                                      DATABASE)  # 连接数据库的uri# mysql+pymysql://{用户名}:{密码}@{host}:{port}/{数据库}?charset=utf8
    engine = create_engine(Db_Uri)  # 连接数据库
    # 创建会话
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    # Session = sessionmaker(bind=engine)
    session = Session()
    print("数据库ORM创建成功")
    return session


def consult_db(db_session, table, field):
    sql_gen = "select name," + field + " from " + table
    cursor_gen = db_session.execute(sql_gen)
    res = cursor_gen.fetchall()  # 这是bqb描述
    return res
