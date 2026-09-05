import re
import json
import read_yaml
import requests
import yaml
import Cam
from huaqiu_order_api.HQPCB.pcb_api import test_hqpcb_order
from huaqiu_order_api.common.my_path import pcb_config_yaml_dir


# import test_hqpcb_order


class Virtualpb:

    def __init__(self):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQJFPCB_URL = data['HQJFPCB_URL']
        self.HEADERS = data['PHPSESSID']
        self.file = '../HQPCB/pcb_mes/cs4.json'
        self.ORDERID = ''
        self.pbid = ''
        self.pb_file  = '../HQPCB/pcb_mes/pb.yaml'

    # 虚拟拼板提取订单
    def pb_extract(self):
        # post请求 url
        post_url = "{}/hqjfpcb/Virtuallist/extract".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id": self.ORDERID}
        ret = requests.post(post_url, data=param_data, headers=headers)
        re_s = re.findall('<h3 class="ui-tipbox-title">([^<>]+)</h3>', ret.text)
        print("[虚拟拼板提取]{}".format(self.ORDERID) + re_s[0])

    # 查询订单内部编号
    def inid_query(self):
        post_url = "{}/hqjfpcb/step/index".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id": self.ORDERID}
        ret = requests.post(post_url, data=param_data, headers=headers)
        # 提供正则表达式获取查询接口返回的pbid（本行代码由全哥赞助）
        # result_pbid = re.findall('P4.*A0', ret.text)
        # 提供正则表达式获取查询接口返回的内部编号
        result_inid = re.findall(r'<!-- <td>\s+([^<>]+)</td> -->', ret.text)
        if result_inid:
            inid = result_inid[0]
            return inid
        else:
            print('未查询到订单：{}'.format(self.ORDERID))

    # 获取json里面数据
    def get_json_data(self):
        inid = Virtualpb.inid_query(self)
        with open(self.file, 'r',
                  encoding='UTF-8') as f:
            json_data = json.load(f)
            datas = json_data["data"]
            for data in datas:
                data["coord"] = ['0.4,0.4,140.0,215.5,90,{} '.format(inid),
                                 '142.0,217.5,140.0,215.5,90,{} '.format(inid)]
            dict = json_data  # 将修改后的内容保存在dict中
            return dict

    # 写入json文件
    def write_json_data(self):
        dict = Virtualpb.get_json_data(self)
        json_str = json.dumps(dict, indent=4, ensure_ascii=False)
        with open(self.file, 'w',
                  encoding='utf-8') as json_file:
            json_file.write(json_str)

    # 上传拼板json文件
    def pb_pass_json(self):
        post_url = "{}/upfile?type=json".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id": "WU_FILE_0", "name": "621813_4L_1.6_2.0oz_.json",
                      "lastModifiedDate": "Mon Feb 27 2023 18:24:25 GMT+0800(中国标准时间)", "size": 799}
        pbfiles = {'file': open(self.file, 'rb')}
        ret = requests.post(post_url, data=param_data, files=pbfiles, headers=headers)
        s = str(ret.json()['status'])

        if s == 'True':
            print('拼板json文件上传成功')
            return ret.json()['url']
        else:
            print('拼板json文件上传失败')

    # 解析json文件
    def pb_parse_json(self):
        json_url = Virtualpb.pb_pass_json(self)
        post_url = "{}/hqjfpcb/VirtualMakeup/parseJson".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param = {"file": json_url}
        ret = requests.get(post_url, params=param, headers=headers)
        par = (ret.json()['data']['selected_option'])
        print(ret.json())
        o_spray = par['o_spray']
        o_blayer = par['o_blayer']
        o_style = par['o_style']
        o_num = par['o_num']
        # print('{}, {}, {}, {}'.format(o_spray, o_blayer, o_style, o_num))
        return o_spray, o_blayer, o_style, o_num

    # pb_parse_json()

    def pb_done(self):
        Virtualpb.pb_extract(self)
        Virtualpb.write_json_data(self)
        json_url = Virtualpb.pb_pass_json(self)
        inid = Virtualpb.inid_query(self)
        o_spray, o_blayer, o_style, o_num = Virtualpb.pb_parse_json(self)
        post_url = "{}/Hqjfpcb/VirtualMakeup/makeimage".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"ooid": self.ORDERID,
                      "count": '{0}+{0}*10.000+10.000*10.000+10.000*1+1*391.5+0.7199999999999989*255.60000000000002+0.7200000000000273*绿色+绿色*白色+白色*90+90*{1}+{1}*++'.format(
                          inid, self.ORDERID),
                      "length": 39.90,
                      "width": 50.40,
                      "pnl": 125,
                      "o_spray": o_spray,
                      "o_blayer": o_blayer,
                      "o_style": o_style,
                      "o_num": o_num,
                      "proportion": 18,
                      "file": json_url,
                      "pnlheight": 504,
                      "pnlwidth": 399,
                      "pre_pnlheight": 520,
                      "pre_pnlwidth": 415,
                      "edge_width": 8,
                      "edge_length": 8,
                      "sel_cid": 0}
        pbfiles = {'file': open(self.file, 'rb')}
        ret = requests.post(post_url, data=param_data, files=pbfiles, headers=headers)
        print(ret.json()['msg'])
        Virtualpb.pbid_query(self)

    # 查询pbid写入yaml文件
    def pbid_query(self):
        post_url = "{}/hqjfpcb/VirtualConfirm/index".format(self.HQJFPCB_URL)
        param_data = {"ktype": 'id', "kvalue": self.ORDERID}
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        ret = requests.post(post_url, data=param_data, headers=headers)
        span = re.findall('<span>([^<>]+)</span>', ret.text)[-1][1]
        if span == '1':
            # 提供正则表达式获取查询接口返回的pbid（本行代码由全哥赞助）
            pbid = re.findall(r'name="pbid"\s+value="([^"]+)"', ret.text)[0]
            data = {self.ORDERID: pbid}
            read_yaml.A.append(self.pb_file, data)
        else:
            print('无数据')

    # 提取订单对应pbid
    def read_pbid(self):
        order_list = read_yaml.A.getyaml(self.pb_file)
        if self.ORDERID in order_list:
            return order_list[self.ORDERID]
        else:
            print(str(self.ORDERID) + '不存在')

    # 虚拟拼板确认拼板
    def pb_sure(self):
        post_url = "{}/hqjfpcb/VirtualConfirm/confirm".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"pbid": self.pbid}
        ret = requests.post(post_url, data=param_data, headers=headers)
        result = re.findall('title">([^<>]+)</h3>', ret.text)
        if result:
            print('[虚拟拼板确认]{}：{}'.format(self.pbid, result[0]))
        else:
            print(print('[虚拟拼板确认]失败订单：{} 不存在该列表'.format(self.ORDERID)))

    # 待提取拼板提取拼板
    def extract_pb(self):
        post_url = "{}/hqjfpcb/Makeup/extract".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"pbid": self.pbid}
        ret = requests.post(post_url, data=param_data, headers=headers)
        result = re.findall('<h3 class="ui-tipbox-title">([^<>]+)</h3>', ret.text)
        if result:

            print('[待提取拼板]提取：{}、{}'.format(self.pbid, result[0]))
        else:
            print('[待提取拼板]提取失败订单：{} 不存在该列表'.format(self.ORDERID))

    # 查询MI制作列表ID
    def miid_query(self):
        post_url = "{}/hqjfpcb/MiCard".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id_type": 'pbid', "id": self.pbid, "mi_status": '-1', "begintime": '', "endtime": '', "cid": -1}
        ret = requests.post(post_url, data=param_data, headers=headers)
        remiid = re.findall('<td rowspan="1">([^<>]+)</td>', ret.text)
        if remiid:
            return remiid[0]
        else:
            return '无MI数据请核实'

    def mi_fz(self):
        mi_id = Virtualpb().miid_query()
        post_url = "{}/hqjfpcb/MiCard/copyCard/navTabId/MiCard".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"mi_id": mi_id, "pbid": 'P4H210764A1'}
        ret = requests.post(post_url, data=param_data, headers=headers)

    def pbgl_sure(self):
        post_url = "{}/hqjfpcb/MakeupManage/confirm/navTabId/MakeupManage".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"pbid": self.pbid, "print_type[{}]".format(self.pbid): 1,
                      "special_note[{}]".format(self.pbid): 'yu', "ajax": 1, "is_iframe": 1, "iframe_confirm": 'false'}
        ret = requests.post(post_url, data=param_data, headers=headers)
        print(ret.json())

    def pbsh_sure(self):
        post_url = "{}/hqjfpcb/MakeupVerify/confirm".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"pbid": self.pbid}
        ret = requests.post(post_url, data=param_data, headers=headers)
        result = re.findall('class="ui-tipbox-title"><p>([^<>]+)</h3>', ret.text)
        print('拼板审核确认成功')

    # MI工序过数方法
    def request_post_MI(self):
        # post请求 url
        self.pbid = Virtualpb.read_pbid(self)
        post_url = "{}/hqjfpcb/UserProcess/scanStep".format(self.HQJFPCB_URL)
        # 请求头部 headers
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        # 请求参数 param_data
        param_data = {"card_number": self.pbid, "process": "MI", "card_end_qty": 500, "batch_no": 1}
        # 发送post请求
        ret = requests.post(post_url, data=param_data, headers=headers)
        #  pass打印接口回参
        jg = (ret.json()['msg'])
        if '成功' in jg:
            pass
        else:
            print(jg)

    # 测试方法添加入库数量
    def putway(self):
        post_url = "{}/test/putway".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param = {"id": self.ORDERID, "qty": 1000}
        ret = requests.get(post_url, params=param, headers=headers)
        print(ret.text)

    # 工程
    def run_pb(self, order_id):
        Cam.Cam().cam_doen(order_id)
        self.ORDERID = order_id
        Virtualpb.pb_done(self)
        self.pbid = Virtualpb.read_pbid(self)
        Virtualpb.pb_sure(self)
        Virtualpb.extract_pb(self)
        Virtualpb.mi_fz(self)
        Virtualpb.pbgl_sure(self)
        Virtualpb.pbsh_sure(self)

    # 工程-MI刷卡-订单入库
    def run_pb_mi_ruku(self, order_id):
        Cam.Cam().cam_doen(order_id)
        self.ORDERID = order_id
        Virtualpb.pb_done(self)
        self.pbid = Virtualpb.read_pbid(self)
        Virtualpb.pb_sure(self)
        Virtualpb.extract_pb(self)
        Virtualpb.mi_fz(self)
        Virtualpb.pbgl_sure(self)
        Virtualpb.pbsh_sure(self)
        Virtualpb.request_post_MI(self)
        Virtualpb.putway(self)

    def run_order_pb(self):
        Virtualpb().run_pb_mi_ruku(int(test_hqpcb_order.PcbOrder().run_order_pay()))

# Virtualpb().putway(1673328)
# VirtualpbMI(1671867).pbgl_sure()
