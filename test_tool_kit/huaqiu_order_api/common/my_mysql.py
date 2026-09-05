import pymysql
import os
from huaqiu_order_api.common.my_Conf import MyConf
from huaqiu_order_api.common.my_path import conf_dir


class MyMysql:

    def __init__(self):
        # 实例化配置类对象
        conf = MyConf(os.path.join(conf_dir, "mysql.ini"))
        # 连接数据库/生成游标
        self.db = pymysql.connect(
            host=conf.get("mysql", "host"),
            user=conf.get("mysql", "user"),
            password=conf.get("mysql", "passwd"),
            port=conf.getint("mysql", "port"),
            database=conf.get("mysql", "database"),
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor
        )

        # 2、创建游标
        self.cur = self.db.cursor()

    def get_count(self, sql):
        # 执行sql
        count = self.cur.execute(sql)
        return count   # 返回的结果是int类型 查询到的结果条数

    def get_one_data(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchone()  # 返回第一条结果  返回的是字典类型

    def get_many_data(self, sql, size=None):
        self.cur.execute(sql)
        if size:
            return self.cur.fetchmany(size)  # 返回指定size条数的数据   是一个列表
        else:
            return self.cur.fetchall()  # 返回所有查询到的数据 是一个列表

    def update_data(self, sql):
        # 事务
        # 提交commit  回滚 rollback
        try:
            self.cur.execute(sql)
        except:
            self.db.rollback()  # 如果出错了就回滚
        else:
            self.db.commit()  # 没出过就提交

    def close_conn(self):
        self.cur.close()  # 关闭游标
        self.db.close()   # 关闭数据库


if __name__ == '__main__':
    conn = MyMysql()
    # sql = "select id from member where mobile_phone='13350000000'"
    # count = conn.get_count(sql)
    # print(count)
    # conn.close_conn()
    sql = "select member.leave_amount from member where id=16"
    res = conn.get_count(sql)
    res1 = conn.get_one_data(sql)
    res2 = conn.get_many_data(sql, 1)
    print(res)
    print(type(res))
    print(res1)
    print(type(res1))
    print(res2)
    print(type(res2))


