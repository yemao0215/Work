import jsonpath
import requests
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
class HQTask:

    def __init__(self, rss, environment=None, task_name=None, match_type=None, action_name=None):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_Task_Center_URL = data['HQCHIP_Task_Center_URL']
        self.environment = environment
        self.task_name = task_name
        self.match_type = match_type
        self.action_name = action_name
        self.json_head = {'Content-Type': 'application/json;charset=UTF-8'}
        self.action_name_json = {"start": "启动", "stop": "停止", "restart": "重启"}
    def task_list(self):
        task_list_url = "{}/api/V2/nodes/".format(self.HQCHIP_Task_Center_URL)
        task_list_res = self.rss.get(url=task_list_url).json()
        server_task_lst = []
        for i in range(len(task_list_res['nodes'])):
            server_name = jsonpath.jsonpath(task_list_res['nodes'][i]['general'], "$..name")[0]
            taskNameInfo = task_list_res['nodes'][i]['processes']
            group_task_name_lst = []
            for a in range(len(taskNameInfo)):
                group_name = taskNameInfo[a]['group']
                task_name = taskNameInfo[a]['name']
                group_task = {"group": group_name, "name": task_name}
                group_task_name_lst.append(group_task)
            server_task = {"name": server_name, "processes": group_task_name_lst}
            server_task_lst.append(server_task)
        return server_task_lst
    def server_task_position(self, server_task_lst):
        processes_name_group_lst = []
        server_processes_name_group_lst_new = []
        if isinstance(server_task_lst, list) and server_task_lst != []:
            # 使用列表推导式
            result = [(item['name'], item['processes']) for item in server_task_lst if self.environment in item['name']]
            for name, processes in result:
                if self.environment in name and isinstance(processes, list):
                    for item in processes:
                        if self.match_type == 1 and item['name'] == self.task_name:
                            processes_name = item['name']
                            processes_group = item['group']
                            processes_name_group_lst.append({"group": processes_group, "name": processes_name})
                        elif self.match_type != 1 and self.task_name in item['name']:
                            processes_name = item['name']
                            processes_group = item['group']
                            processes_name_group_lst.append({"group": processes_group, "name": processes_name})
                    server_processes_name_group_lst_new.append((name, processes_name_group_lst))
                    break
        return server_processes_name_group_lst_new
    def task_action_Execution(self, action_name, server_name, group,task_name):
        task_action_Execution_url = ''
        if action_name == "start":
            task_action_Execution_url = "{}/api/V2/nodes/{}/processes/{}:{}/start".format(self.HQCHIP_Task_Center_URL, server_name, group, task_name)
        elif action_name == "stop":
            task_action_Execution_url = "{}/api/V2/nodes/{}/processes/{}:{}/stop".format(self.HQCHIP_Task_Center_URL, server_name, group, task_name)
        elif action_name == "restart":
            task_action_Execution_url = "{}/api/V2/nodes/{}/processes/{}:{}/restart".format(self.HQCHIP_Task_Center_URL, server_name, group, task_name)
        task_action_Execution_res = self.rss.get(url=task_action_Execution_url, headers=self.json_head).json()
        msg = ''
        if task_action_Execution_res['status'] == 'success':
            for k, v in self.action_name_json.items():
                if k == action_name:
                    msg = "执行服务器：{}的任务名：{}执行动作：{}成功".format(server_name, task_name,v)
                    logger.info(msg)
        return msg
    def mian_environment_match_task(self):
        msg = ''
        msg_list = []
        server_task_lst = self.task_list()
        server_processes_name_group_lst_new = self.server_task_position(server_task_lst)
        for name, task_group_lst in server_processes_name_group_lst_new:
            if isinstance(task_group_lst, list) and task_group_lst != []:
                for item in task_group_lst:
                    msg_lst = self.task_action_Execution(self.action_name, name, item['group'], item['name'])
                    msg_list.append(msg_lst)
                msg = msg_list
            else:
                msg = "执行服务器：{}的任务名：{}不存在，请检查任务名称或者匹配类型".format(name, self.task_name)
        return msg