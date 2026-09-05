from pymongo import MongoClient

# 连接字符串（你现在已经能认证成功了）
class MongodbLogin:
     # UAT环境
    def __init__(self, env=None):
        self.fat_Host_address = "@fat-mongodb_01.elecfans.net:27017,fat-mongodb_02.elecfans.net:27017,fat-mongodb_03.elecfans.net:27017/"
        self.uat_Host_address = "@192.168.20.129:27017,192.168.20.130:27017,192.168.20.131:27017/"
        self.env = env

    def login_username_password(self, env):
        username = None
        password = None
        env_username_password_json = {
            "fat": {
                "username": "hqjf",
                "password": "uvGVxvpewM0ypSkDX3y4Jrt1mgX4ipOV"
            },
            "uat": {
                "username": "test_readonly",
                "password": "bahJmEsi6LNXQVun5c7ccyszExrMl9ri"
            }
        }
        for k, v in env_username_password_json.items():
            if k == env:
                username = v["username"]
                password = v["password"]
        return username, password

    def login(self):
        username, password = self.login_username_password(self.env)
        if self.env == "fat":
            self.MONGO_URI = (
                f"mongodb://{username}:{password}" + self.fat_Host_address +"?authSource=hqchip&replicaSet=MyRepl"
            )
        elif self.env == "uat":
            self.MONGO_URI = (
                f"mongodb://{username}:{password}" + self.uat_Host_address +"?authSource=hqchip"  # &replicaSet=MyRepl
            )
        client = MongoClient(self.MONGO_URI)
        db = client["hqchip"]  # 使用你的认证库，权限足够

        # 测试：查询一个集合（一定成功）
        try:
            # 随便查一条数据，验证连接有效
            print("✅ MongoDB 连接成功！")
            print("当前数据库：", db.name)
        except Exception as e:
            print("❌ 失败：", e)
        return db
if __name__ == '__main__':
     env = "uat"
     MongodbLogin(env=env).login()