import requests
import re
import yaml

from huaqiu_order_api.common.my_path import pcb_config_yaml_dir

""""外协（CAM）处理模块
1.查询订单工程状态（cam_status）-->2.cam取单(cam_extract)-->3.上传工程文件（cam_camfile）-->4.cam完成(cam_doen())
"""


class Cam:
    def __init__(self):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQJFPCB_URL = data['HQJFPCB_URL']
        self.HEADERS = data['PHPSESSID']

    # 查询订单工程状态
    def cam_status(self, order_id):
        post_url = "{}/hqjfpcb/Virtuallist/index".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id": order_id}
        ret = requests.post(post_url, data=param_data, headers=headers)
        style = re.findall('<tr style="([^"]+):#fff">', ret.text)
        if style:
            color = re.findall('<td><font color="([^"]+)"', ret.text)[0]
            project_status = re.findall('<td><font color="{}">([^<>]+)</font></td>'.format(color), ret.text)[0]
            if '已处理' in project_status:
                print(project_status)
            else:
                print('订单：{}，{}'.format(order_id, project_status))
                # 工程未处理时，再次调用CAM完成接口
                Cam.cam_doen(self, order_id)
        else:
            print('订单：{} 不存在'.format(order_id))

    # cam取单
    def cam_extract(self, order_id):
        post_url = "{}/hqjfpcb/Camlist/extract/".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id": order_id}
        ret = requests.post(post_url, data=param_data, headers=headers)
        re_s = re.findall('<h3 class="ui-tipbox-title">([^<>]+)</h3>', ret.text)
        print(re_s[0])

    # 上传工程文件
    def cam_camfile(self, order_id):
        post_url = "{}/test/camfile".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param = {"id": order_id}
        ret = requests.get(post_url, params=param, headers=headers)
        print(ret.text)

    # cam完成
    def cam_doen(self, order_id):
        Cam.cam_extract(self, order_id)
        Cam.cam_camfile(self, order_id)
        post_url = "{}/hqjfpcb/Outsource/submitFinish/navTabId/Outsource".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {
            "id": order_id,
            "konghuan{}".format([order_id]): 3.5,
            "min_line_width{}".format([order_id]): 5.50,
            "min_wire_space{}".format([order_id]): 5.60,
            "tongkong{}".format([order_id]): 6.5,
            "min_zuankong{}".format([order_id]): 1,
            "min_bga{}".format([order_id]): 3,
            "min_ic_bridge_width{}".format([order_id]): 3,
            "min_ic_width{}".format([order_id]): 3,
            "min_hole_wall_space{}".format([order_id]): 3,
            "inside_min_line_width{}".format([order_id]): 3,
            "inside_min_wire_space{}".format([order_id]): 3,
            "midhole_to_conductor{}".format([order_id]): 3,
            "has_period{}".format([order_id]): 1,
            "period_format{}".format([order_id]): 1,
            "first_spray{}".format([order_id]): 2,  # 先喷锡后文字 1：是，2：否
            "max_metal_slot_x{}".format([order_id]): 3,
            "max_metal_slot_y{}".format([order_id]): 12,
            "vcut{}".format([order_id]): 2,
            "vcut_surplus_thickness{}".format([order_id]): 0.4,
            "vcut_angle{}".format([order_id]): 30,
            "vcut_tolerance{}".format([order_id]): "",
            "xknives_nums{}".format([order_id]): "",
            "yknives_nums{}".format([order_id]): "",
            "ajax": 1,
            "is_iframe": 1,
            "iframe_confirm": 1,
            "special_period{}".format([order_id]): 1  # 特殊生产周期 1是 2否
        }
        ret = requests.post(post_url, data=param_data, headers=headers)
        jg = ret.json()['info']
        print(ret.json())
        if '提交成功' in jg:
            print('订单：{}，{}'.format(order_id, jg))
            # 查询CAM是否完成
            Cam.cam_status(self, order_id)
        else:
            print('订单：{}，{}'.format(order_id, jg))

    # cam撤回
    def cam_withdraw(self, order_id):
        post_url = "{}/hqjfpcb/Complete/notpass".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"id": order_id, "internalmsg": 2}
        ret = requests.post(post_url, data=param_data, headers=headers)
        print(ret.text)

    def eq_scg(self, order_id):
        post_url = "{}/hqjfpcb/errororder/confirmFile/navTabId/ErrorOrder".format(self.HQJFPCB_URL)
        headers = {"Cookie": "PHPSESSID={}".format(self.HEADERS), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        param_data = {"order_id": order_id, "agree": 1}
        ret = requests.post(post_url, data=param_data, headers=headers)





