# coding:UTF-8

import pymysql


class DbManager:
    # 构造函数
    def __init__(self, host='127.0.0.1', port=3306, user='root',
                 password='abcd', dbname='isrbqb', charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.charset = charset
        self.conn = None
        self.cur = None

    # 连接数据库
    def connect_database(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port,
                                        user=self.user, passwd=self.password,
                                        db=self.dbname, charset=self.charset)
        except:
            print("connect_database failed")
            return False
        self.cur = self.conn.cursor()
        return True

    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    # 执行数据库的sq语句,主要用来做插入操作
    def execute(self, sql_str, params=None, commit=False):
        # 连接数据库
        res = self.connect_database()
        # 记录受影响的行数
        rowcount = 0

        if not res:
            return False
        # try:
        if self.conn and self.cur:
            # 正常逻辑，执行sql，提交操作
            rowcount = self.cur.execute(sql_str, params)
            if commit:
                self.conn.commit()
            else:
                pass
        # except:
        #     print("execute failed: " + sql_str)
        #     print("params: " + str(params))
        #     self.close()
        #     return False
        return rowcount

    # 查询所有数据
    def fetchall(self, sql_str, params=None):
        res = self.execute(sql_str, params)
        if not res:
            print("查询失败")
            return False
        self.close()
        results = self.cur.fetchall()
        print("查询成功" + str(results))
        # 返回结果的元组
        return results

    # 查询一条数据
    def fetchone(self, sql_str, params=None):
        res = self.execute(sql_str, params)
        if not res:
            print("查询失败")
            return False
        self.close()
        one_result = self.cur.fetchone()
        # print("查询成功" + str(one_result))
        return one_result

    # 增删改数据
    def edit(self, sql_str, params=None):
        res = self.execute(sql_str, params, True)
        if not res:
            print("操作失败")
            return False
        self.conn.commit()
        self.close()
        print("操作成功" + str(res))
        return res
