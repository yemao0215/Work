import json
import re
import time
from datetime import datetime

import jsonpath
from urllib.parse import quote, urlencode
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_Activity.big_data.user_promotion import UserPromotion
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ProjectBuildJenkins:
    def __init__(self, rss, environment=None, project_name=None, publish_branch=None):
        self.rss = rss
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {"Content-Type": "application/x-www-form-urlencoded"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Jenkins_URL = data['Jenkins_URL']
        self.environment = environment
        self.project_name = project_name
        self.publish_branch = publish_branch
    def custom_quote(self, s):
        """自定义编码函数，强制编码斜杠"""
        encoded = quote(s)
        return encoded.replace('/', '%2F')
    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def query_url_arguments_new(self, data):
        """将嵌套字典转成为查询字符串，其中嵌套对像作为JSON字符串传递"""
        parts = []
        for k, v in data.items():
            # 如果值是字典或列表，则将其转换为JSON字符串
            if isinstance(v, dict) or isinstance(v, list):
                # 转换为JSON字符串(保持与浏览器格式一致)
                json_v = json.dumps(v, separators=(', ', ': '), ensure_ascii=False)
                # JSON字符串进行URL编码
                encoded_JSON = self.custom_quote(json_v)
                parts.append(k + '=' + encoded_JSON)
            else:
                parts.append(k + '=' + quote(str(v)))
        query_string = '&'.join(parts)
        return query_string
    def project_location_split(self):
        """拼接项目地址以及获取Jenkins_Crumb"""
        self.project_location_split_url = "{0}/job/{1}/job/{2}".format(self.Jenkins_URL, self.environment, self.project_name)
        project_location_split_res = self.rss.get(url=self.project_location_split_url).text
        try:
            Jenkins_Crumb_value = re.search(r'data-crumb-value="(.*?)"', project_location_split_res).group(1)
            setattr(Data, "Jenkins_Crumb_value", Jenkins_Crumb_value)
            return True
        except:
            logger.error(f"{self.project_name}在执行环境：{self.environment}不存在，请跟运维核对对应项目的项目实际名称")
            return False
    def project_branch_comparison(self):
        """发布项目分支定位"""
        project_branch_url = "{}/descriptorByName/net.uaznia.lukanus.hudson.plugins.gitparameter.GitParameterDefinition/fillValueItems?param=branch".format(self.project_location_split_url)
        project_branch_res = self.rss.get(url=project_branch_url, headers=self.form_head).json()
        branch_name = jsonpath.jsonpath(project_branch_res, "$..name")
        branch_value = jsonpath.jsonpath(project_branch_res, "$..value")
        branch_name_1_value_json = None
        branch_name_2_value_json = None
        project_name_actual = {"hq_center_web": ["hq_center_web", "order_component"]}
        if self.project_name in project_name_actual:
            project_name_actual_lst = project_name_actual[self.project_name]
            project_brand_url = "{}/descriptorByName/net.uaznia.lukanus.hudson.plugins.gitparameter.GitParameterDefinition/fillValueItems?param={}".format(
                self.project_location_split_url, project_name_actual_lst[0])
            project_1_brand_res = self.rss.get(url=project_brand_url, headers=self.form_head).json()
            branch_1_name = jsonpath.jsonpath(project_1_brand_res, "$..name")
            branch_1_value = jsonpath.jsonpath(project_1_brand_res, "$..value")
            branch_name_1_value_json = {project_name_actual_lst[0]: dict(zip(branch_1_name, branch_1_value))}
            project_brand_url = "{}/descriptorByName/net.uaznia.lukanus.hudson.plugins.gitparameter.GitParameterDefinition/fillValueItems?param={}".format(
                self.project_location_split_url, project_name_actual_lst[1])
            project_2_brand_res = self.rss.get(url=project_brand_url, headers=self.form_head).json()
            branch_2_name = jsonpath.jsonpath(project_2_brand_res, "$..name")
            branch_2_value = jsonpath.jsonpath(project_2_brand_res, "$..value")
            branch_name_2_value_json = {project_name_actual_lst[1]: dict(zip(branch_2_name, branch_2_value))}
        if branch_name_1_value_json != None and branch_name_2_value_json != None:
                branch_name_value_json = [branch_name_1_value_json, branch_name_2_value_json]
        else:
                branch_name_value_json = dict(zip(branch_name, branch_value))
        self.publish_branch_value = ''
        # 增加匹配计数器
        count = 0
        if isinstance(branch_name_value_json, dict):
            for k in branch_name_value_json:
                if self.publish_branch in k:
                    count += 1
            if count > 1:
                # 当发布分支匹配分支字典存在多个时，走完全全等发布分支
                for v in branch_name_value_json:
                    if self.publish_branch == v:
                        self.publish_branch_value = branch_name_value_json[v]
                        break
                    elif "origin/" + self.publish_branch == v:
                        self.publish_branch_value = branch_name_value_json[v]
                        break
            elif count == 1:
                # 当发布分支匹配分支字典仅存在1个时，走匹配发布分支
                for m in branch_name_value_json:
                    if self.publish_branch in m:
                        self.publish_branch_value = branch_name_value_json[m]
                        break
        elif isinstance(branch_name_value_json, list):
            publish_branch_value_count = []
            publish_branch_value = ""
            for z in range(len(branch_name_value_json)):
                for a, b in branch_name_value_json[z].items():
                    for c in b:
                        if self.publish_branch in c:
                            count += 1
                    if count > 1:
                        for v in b:
                            if self.publish_branch == v:
                                publish_branch_value = b[v]
                                break
                            elif "origin/" + self.publish_branch == v:
                                publish_branch_value = b[v]
                                break
                    elif count == 1:
                        for m in b:
                            if self.publish_branch in m:
                                publish_branch_value = b[m]
                                break
                    elif count == 0:
                        if a == "order_component" and "fat" in self.publish_branch:
                            for m in b:
                                if "smt/fat" in m:
                                    publish_branch_value = b[m]
                                    break
                        elif a == "order_component" and "uat" in self.publish_branch:

                            for m in b:
                                if "pcb/uat" in m:
                                    publish_branch_value = b[m]
                                    break

                    publish_branch_value = {a: publish_branch_value}
                    publish_branch_value_count.append(publish_branch_value)
                    count = 0
            self.publish_branch_value = publish_branch_value_count
        print("获取到实际需要执行的项目分支：{}".format(self.publish_branch_value))
        return self

    def build_project_branch(self):
        if self.publish_branch_value != '':
            Jenkins_Crumb_value = getattr(Data, "Jenkins_Crumb_value")
            logger.info("Jenkins_Crumb_value：{}".format(Jenkins_Crumb_value))
            build_project_branch_url = "{}/build?delay=0sec".format(self.project_location_split_url)
            logger.info("执行项目链接：{}".format(build_project_branch_url))
            build_project_branch_body = {"name": "branch", "value": self.publish_branch_value, "statusCode": "303", "redirectTo": ".", "Jenkins-Crumb": Jenkins_Crumb_value,
                                         "json": {"parameter": {"name": "branch", "value": self.publish_branch_value}, "statusCode": "303", "redirectTo": ".", "Jenkins-Crumb": Jenkins_Crumb_value},
                                         "Submit": "开始创建"}
            parameter_values = []
            names = None
            values = None
            if isinstance(self.publish_branch_value, list):
                del build_project_branch_body["name"]
                del build_project_branch_body["value"]
                names = [key for d in self.publish_branch_value for key in d.keys()]
                values = [value for d in self.publish_branch_value for value in d.values()]
                for i in range(len(self.publish_branch_value)):
                    for k, j in self.publish_branch_value[i].items():
                        parameter = {"name": k, "value": j}
                        parameter_values.append(parameter)
                json_vaule_1 = build_project_branch_body["json"]
                json_vaule_1["parameter"] = parameter_values
            if self.project_name in [
                                    "hqchip",
                                    "hqchip_admin",
                                    "hqchip_product",
                                    "hq_activity",
                                    "hq_activity_web",
                                    "hc2018_admin",
                                    "hqchip_admin_new",
                                    "hqchiperp",
                                    "hqchip_search",
                                    "hqchip_es_service",
                                    "hqchip_partner",
                                    "hqchip_partner_web"
                                    "hqchip_erp_sync",
                                    "hqchipapi",
                                    "hqchipscripts",
                                    "hq_dfm",
                                    "dfm_web",
                                    "sso",
                                    "hqpcb",
                                    "elecfans",
                                    "hq_center_web",
                                    "hqchip_trade",
                                    "activity_web",
                                    "product_page_pc",
                                    "product_page_m",
                                    "wms_model",
                                    "wms-business",
                                    "wms-warehouse",
                                    "wms_report",
                                    "hqchip_ai_api",
                                    "smt",
                                    "approval_service",
                                    "crm_web",
                                    "center_service",
                                    "hqdoc_service"
            ]:
                new_dict = {"name": "env", "value": "hqchip_web_01"}
                new_dict = self.env_value_replace(new_dict)
                json_vaule = build_project_branch_body["json"]
                parameter_value = json_vaule["parameter"]
                # 将原始字典转换为列表形式
                if not isinstance(parameter_value, list):
                    parameter_value_list = [parameter_value]  # 如果原始值不是列表，则将其转换成列表形式
                    json_vaule["parameter"] = parameter_value_list  # 更新字典中的值为列表形式
                else:
                    parameter_value_list = parameter_value
                if self.project_name in ["hqchip_admin_new", "wms_model", "wms-business", "wms-warehouse", "hqchip_es_service"] and self.environment == "uat":
                    # hqchip_admin_new uat 不需要new_dict，跳过
                    pass
                elif self.project_name in ["hqchip_trade", "activity_web", "product_page_pc", "product_page_m", "wms_model", "crm_web", "hqdoc_service", "hq_center_web"]:
                        pass
                else:
                    if new_dict != {}:
                        parameter_value_list.append(new_dict)
                if self.project_name in ["hqchip_es_service", "wms_model", "wms-business", "wms-warehous", "wms_report"]:
                    if self.project_name in ["wms-business", "wms-warehous", "wms_report"] and  self.environment == "uat":
                        pass
                    else:
                        new_dict1 = {"name": "JAVA_HOME", "value": "/usr/local/jdk-11.0.12"}
                        parameter_value_list.append(new_dict1)
            # hq_center_web 特殊化
            if names != None and values != None:
                params = []
                for n, v in zip(names, values):
                    params.append(("name", n))
                    params.append(("value", str(v)))
                # query_name_value = "&".join(["{}={}".format(k, v) for k, v in params])
                query_name_value_string = urlencode(params) + "&"
                build_project_branch_body_1 = self.query_url_arguments(build_project_branch_body)
                build_project_branch_url = query_name_value_string + build_project_branch_body_1
            else:
                build_project_branch_body = self.query_url_arguments(build_project_branch_body)
            build_project_branch_res = self.rss.get(url=build_project_branch_url, data=build_project_branch_body, headers=self.form_head)
            code = build_project_branch_res.status_code
        else:
            code = "发布分支在执行环境不存在，请检查发布分支"
        return code
    def env_value_replace(self, new_dict):
        if self.project_name in ["hqchip", "hqchip_product", "hqchiperp", "hqchip_search", "hqchip_partner", "hqchip_partner_web",
                                 "hq_dfm", "dfm_web", "wms-business", "wms-warehouse"]:
            if self.project_name == "dfm_web":
                new_dict["value"] = f"hq_{self.project_name}_web_01"
            elif self.project_name == "hqchip_partner_web":
                new_dict["value"] = f"hq_{self.project_name}_01"
            else:
                new_dict["value"] = f"{self.project_name}_web_01"
        elif self.project_name in ["hqchip_admin", "hqpcb", "smt"]:
            if self.environment == "fat":
                new_dict["value"] = f"{self.project_name}_web_01"
            else:
                # 使用三元条件表达式来判断是否存在下划线
                # self.project_name.split("_")[0] if "_" in self.project_name else self.project_name
                new_dict["value"] = "release_{}".format(self.project_name.split("_")[0] if "_" in self.project_name else self.project_name)
                if self.environment == "smt":
                    new_dict["value"] = "192.168.19.211 hqchip_web_01"
        elif self.project_name == "sso":
            if self.environment == "fat":
                new_dict["value"] = "sso_web_01"
            else:
                new_dict["value"] = "sso_web"
        elif self.project_name in ["hqchip_erp_sync", "hqchipapi", "hqchipscripts", "hqchip_ai_api"]:
            if self.environment == "fat" and self.project_name != "hqchip_ai_api":
                new_dict["value"] = "hqchip_python2"
            elif  self.environment == "fat" and self.project_name == "hqchip_ai_api":
                new_dict["value"] = "hqchip_python3"
            else:
                new_dict["value"] = "release_python"
        elif self.project_name in ["hqchip_es_service", "hq_center_web"]:
            if self.environment == "fat" and self.project_name == "hqchip_es_service":
                new_dict["value"] = "192.168.18.131 hqchip_search_web_01"
            else:
                new_dict = {}
        elif self.project_name in ["hq_activity", "hq_activity_web"]:
            if self.environment == "fat":
                new_dict["value"] = "hq_activity_web_01"
            else:
                new_dict["value"] = "java_bom_match_service_01"
        elif self.project_name in ["hc2018_admin", "hqchip_admin_new"]:
            if self.environment == "fat":
                new_dict["value"] = "hc2018_admin_web_01"
            else:
                if self.project_name == "hc2018_admin":
                    new_dict["value"] = "hc2018_admin_01"
        elif self.project_name in ["elecfans"]:
            if self.environment == "fat":
                new_dict["value"] = "elecfans_web_01"
            else:
                new_dict["value"] = "192.168.20.163-elecfans_web_02"
        elif self.project_name in ["wms_report"]:
            if self.environment == "fat":
                new_dict["value"] = "wms_report_web_01"
            else:
                new_dict["value"] = "wms-base_web_01"
        elif self.project_name in ["center_service"]:
            new_dict["value"] = "customer-center_web_01"
        return new_dict

    def mian_build_project(self):
        result = self.project_location_split()
        if result == True:
            self.project_branch_comparison()
            code = self.build_project_branch()
        else:
            code = f"{self.project_name}在执行环境：{self.environment}不存在，请跟运维核对对应项目的项目实际名称"
        return code



