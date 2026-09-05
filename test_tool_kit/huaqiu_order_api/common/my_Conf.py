from configparser import ConfigParser


class MyConf(ConfigParser):

    def __init__(self, filepath):  # 定义子类私有方法，会覆盖父类私有方法
        super().__init__()  # 通过supper().__init__() 重新继承父类的私有方法
        self.read(filepath, encoding="utf-8")  # 读文件







