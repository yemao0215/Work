import requests, time, json, threading


class Presstest(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Content-Type': 'application/json;',
    }


    def __init__(self, login_url, biz_url, account, password, data):
        self.login_url = login_url
        self.biz_url = biz_url
        self.account = account
        self.password = password
        self.data = data
        self.session = requests.Session()
        self.session.headers = self.headers
        self.json_headers = {'Content-Type': "application/json;"}

    # 登录
    # def login(self):
    #     '''登陆获取session'''
    #     source_data = source_data = {'t': int(time.time() * 1000), 'account': self.account, 'password': self.password}
    #     res = self.session.post(self.login_url, source_data=json.dumps(source_data))
    #     # 判断登录接口响应码
    #     if res.json().get('code') == 200:
    #         print(threading.current_thread().name, '登录成功\n')
    #     else:
    #         print(threading.current_thread().name, '登录失败，原因：', res.json(), '\n')
    #     # 获取token并设置请求头
    #     XToken = res.json().get('source_data').get('xxx_token')
    #     self.session.headers['token'] = XToken

    # 调用目标方法
    def testinterface(self):
        '''压测接口'''
        global ERROR_NUM
        try:

            t1 = time.time()
            # 调用post接口
            # html = self.session.post(self.biz_url, json.dumps(self.source_data))
            html = requests.post(self.biz_url, json.dumps(self.data), headers=self.json_headers)
            t2 = time.time()
            if html.json().get('result') != None:
                print(threading.current_thread().name, '请求成功，耗时：', t2 - t1, '\n')
                # 打印响应信息
                # print(threading.current_thread(), '请求成功，耗时：', t2-t1, '响应：', html.json(), '\n')
            else:
                print(threading.current_thread().name, '请求失败，原因：', html.json(), '\n')
                ERROR_NUM += 1
        except Exception as e:
            print(e)
            ERROR_NUM += 1

    # 单线程内循环调用目标方法
    def testonework(self):
        '''一次并发处理单个任务'''
        i = 0
        while i < ONE_WORKER_NUM:
            i += 1
            self.testinterface()
        time.sleep(LOOP_SLEEP)


    # 启动多个线程
    def run(self):
        '''使用多线程进程并发测试'''
        t1 = time.time()
        Threads = []

        for i in range(THREAD_NUM):
            t = threading.Thread(target=self.testonework, name="T" + str(i))
            # t.setDaemon(True)过时
            t.daemon = True
            Threads.append(t)

        for t in Threads:
            t.start()
        for t in Threads:
            t.join()
        t2 = time.time()

        print("===============压测结果===================")
        print("URL:", self.biz_url)
        print("任务数量:", THREAD_NUM, "*", ONE_WORKER_NUM, "=", THREAD_NUM * ONE_WORKER_NUM)
        print("总耗时(秒):", t2 - t1)
        print("每次请求耗时(秒):", (t2 - t1) / (THREAD_NUM * ONE_WORKER_NUM))
        print("每秒承载请求数:", (THREAD_NUM * ONE_WORKER_NUM) / (t2 - t1))
        print("错误数量:", ERROR_NUM)


if __name__ == '__main__':
    # 登录url
    login_url = 'https://xxx.com/api/xxx/login'
    # 登录用户名
    account = "xxx"
    # 登录密码
    password = "xxx"

    # 压测url
    biz_url = 'https://uat-item.hqchip.com/api/v2/substitute/getSubstituteList'

    # 请求参数 java接口需@RequestBody接收参数，否则无法解析
    data = {
    "pageNum" :1,
    "pagesize" : 6,
    # "disableCache" : False
}

    THREAD_NUM = 3  # 并发线程总数
    ONE_WORKER_NUM = 100  # 每个线程的循环次数
    LOOP_SLEEP = 1  # 每次请求时间间隔(秒)
    ERROR_NUM = 0  # 出错数

    obj = Presstest(login_url=login_url, biz_url=biz_url, account=account, password=password, data=data)
    # obj.login()
    obj.run()

    # 运行后不自动关闭窗口
    input('Press Enter to exit...')

