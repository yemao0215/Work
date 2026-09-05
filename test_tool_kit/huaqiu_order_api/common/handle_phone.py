from faker import Faker
from huaqiu_order_api.common.my_mysql import MyMysql


def get_new_phone():
    """
    使用faker生成手机号码
    调用mysql数据库操作，去判断是否在数据中存在。如果不在，表示没有注册
    return:
    """
    # while True:
        # phone = Faker("zh_CN").phone_number()  # 调用faker中文简体 手机号方法  随机生成手机号码
        # sql = "select id from member where mobile_phone='{}'".format(phone)
        # res = MyMysql().get_count(sql)  # 调用封装的方法执行sql语句 返回的是查询到的数据行数
        # if res == 0:  # 数据库查询到的行数是0 表示该手机号码没有被注册过
        # return phone  # 返回生成的手机号码，并且结束循环
    fk = Faker("zh_CN")

    print(fk.name())


    number = fk.phone_number()
    print('生成手机号:',number)
    # number = fake.phone_number()
    # number


def is_exist_phone(phone_num):
    """
    调用mysql数据库操作，去判断手机号是否存在；如果不在，表示没有注册
    """
    sql = "select id from member where mobile_phone='{}'".format(phone_num)
    res = MyMysql().get_count(sql)
    if res == 0:
        return False
    else:
        return True


if __name__ == "__main__":
    txt = "Hello,welcome to my world."

    x = txt.index("welcome")
    print(x)
    get_new_phone()

