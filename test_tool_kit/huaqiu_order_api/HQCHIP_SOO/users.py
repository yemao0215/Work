import json
import math
import pandas as pd
import jsonpath
import requests
import yaml
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, auth_users_test_dir, auth_users_formal_dir


class SOOUsers:
    def __init__(self, target_rss=None, environment=None):
        """
        :param environment: 执行环境 pro/uat/fat
        :return:
        """
        self.rss = target_rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Auth_Base_URL = data['Auth_Base_URL']
        self.json_head = {"Content-Type": "application/json"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9",
                                  "Connection": "keep-alive"}

        self.environment = environment
        if self.environment == "pro":
            self.Auth_Base_URL = data['Auth_Base_Pro_URL']
            print(self.Auth_Base_URL)

    def get_org_info(self, org):
        """
        递归函数，用于获取组织架构树中所有节点的信息

        :param childOrg: 子节点列表
        :return: 节点信息列表
        """
        org_info = {"name": org["name"], "id": org["id"], "parentId": org["parentId"]}
        orgs = []
        orgs = [org_info]
        if org["childOrg"]:
            for child in org["childOrg"]:
                orgs.extend(self.get_org_info(child))
        return orgs

    def extract_org_info(self, org, level):
        org_info = {
            'name': org['name'],
            'id': org['id'],
            'parentId': org['parentId']
        }
        if 'childOrg' in org:
            org_info['child'] = []
            for child in org['childOrg']:
                org_info['child'].append(self.extract_org_info(child, level + 1))
        return org_info

    def extract_leaf_departments(self, department, leaf_departments):
        if "child" not in department or len(department["child"]) == 0:
            leaf_departments.append(department)
        else:
            for child_department in department["child"]:
                self.extract_leaf_departments(child_department, leaf_departments)
    def get_department(self):
        """部门"""
        search_company_url = "{}/orgauth/company/getAllBrief".format(self.Auth_Base_URL)
        search_company_res = self.rss.get(search_company_url, headers=self.json_head)
        company_appKey = jsonpath.jsonpath(search_company_res.json(), '$..appKey')
        company_name = jsonpath.jsonpath(search_company_res.json(), '$..name')
        company_no = jsonpath.jsonpath(search_company_res.json(), '$..no')
        # 使用 zip() 函数将三个列表合并成一个元组列表，然后通过循环遍历这个元组列表，创建字典
        companies_dict = {name: {"company_appKey": appKey, "company_no": no} for name, appKey, no in
                          zip(company_name, company_appKey, company_no)}
        company_no_list = [company['company_no'] for company in companies_dict.values()]
        # print(company_no_list)
        company_name_list = list(companies_dict.keys())
        # print(company_no_list)
        leaf_departments_id = []  # 末级组织数据
        company_leaf_departments_id_dict = []  # 公司与末级组织对应的字典
        for m in range(len(company_no_list)):
            # print(type(company_no_list[m]))
            if "uat" in self.Auth_Base_URL or "fat" in self.Auth_Base_URL:
                search_department_url = "{}/orgauth/org/page".format(self.Auth_Base_URL)
                search_department_body = {"companyNo": company_no_list[m], "name": ""}
                search_department_res = self.rss.post(search_department_url, json=search_department_body, headers=self.json_head).json()
                department_dict_1 = []  # 不含层级部门组织数据
                department_dict = []  # 含层级部门组织数据
                for i in range(len(search_department_res["result"])):
                    result = search_department_res["result"][i]
                    info = self.get_org_info(result)
                    department_dict_1 = department_dict_1 + info
                    org_info = self.extract_org_info(result, 0)
                    department_dict = department_dict + [org_info]

                # res_json = json.dumps(department_dict_1, ensure_ascii=False).replace("'", '"')
                # print(res_json)
                leaf_departments = []
                for department in department_dict:
                    self.extract_leaf_departments(department, leaf_departments)
                for leaf_department in leaf_departments:
                    leaf_departments_id.append(leaf_department["id"])
                company_leaf_departments_id = {company_name_list[m]: leaf_departments_id}
                company_leaf_departments_id_dict.append(company_leaf_departments_id)
                print(company_leaf_departments_id_dict)
            else:
                # print(company_no_list[m])
                if company_no_list[m] == 1001:
                    search_department_url = "{}/orgauth/org/page".format(self.Auth_Base_URL)
                    search_department_body = {"companyNo": company_no_list[m], "name": ""}
                    search_department_res = self.rss.post(search_department_url, json=search_department_body,
                                                          headers=self.json_head).json()
                    department_dict_1 = []  # 不含层级部门组织数据
                    department_dict = []  # 含层级部门组织数据
                    for i in range(len(search_department_res["result"])):
                        result = search_department_res["result"][i]
                        info = self.get_org_info(result)
                        department_dict_1 = department_dict_1 + info
                        org_info = self.extract_org_info(result, 0)
                        department_dict = department_dict + [org_info]
                    # print(f"1112： {department_dict_1}")
                    # print(f"1111： {department_dict}")
                    # res_json = json.dumps(department_dict_1, ensure_ascii=False).replace("'", '"')
                    # print(res_json)
                    leaf_departments = []
                    for department in department_dict:
                        self.extract_leaf_departments(department, leaf_departments)
                    # print(leaf_departments)
                    for leaf_department in leaf_departments:
                        leaf_departments_id.append(leaf_department["id"])
                    company_leaf_departments_id = {company_name_list[m]: leaf_departments_id}
                    company_leaf_departments_id_dict.append(company_leaf_departments_id)
        print(company_leaf_departments_id_dict)

        return company_leaf_departments_id_dict
    def get_users(self, company_leaf_departments_id_dict):
        """用户"""
        search_user_url = "{}/orgauth/employee/findEmployeeByOrgId".format(self.Auth_Base_URL)
        employee_code_count = []
        employee_mobile_count = []
        employee_dep_name_count = []
        employee_name_count = []
        employee_id_count = []
        employee_dep_id_count = []
        employee_status_count = []
        # print(company_leaf_departments_id_dict)
        for i in company_leaf_departments_id_dict:
            # print(i)
            # print(i.items())
            for key, value in i.items():
                search_user_body = {"beMain": "", "companyName": key, "counted": True, "orgIds": "", "pageNum": 1,
                                    "pageSize": 10, "searchContext": "", "type": ""}
                for j in value:
                    search_user_body["orgIds"] = j
                    # print(search_user_body)
                    search_user_res = self.rss.post(url=search_user_url, json=search_user_body, headers=self.json_head).json()
                    # print(search_user_res)
                    total = int(jsonpath.jsonpath(search_user_res, '$..total')[0])
                    if math.ceil(total / 10) >= 1:
                        total_num = math.ceil(total / 10)
                        for m in range(total_num):
                            m = m + 1
                            search_user_body["pageNum"] = m
                            search_user_res = self.rss.post(url=search_user_url, json=search_user_body, headers=self.json_head).json()
                            employee_code = jsonpath.jsonpath(search_user_res, '$..code')
                            employee_mobile = jsonpath.jsonpath(search_user_res, '$..mobile')
                            employee_dep = jsonpath.jsonpath(search_user_res, '$..orgName')
                            employee_name = jsonpath.jsonpath(search_user_res, '$..realName')
                            employee_id = jsonpath.jsonpath(search_user_res, '$..id')
                            employee_dep_id = jsonpath.jsonpath(search_user_res, '$..orgId')
                            employee_status = jsonpath.jsonpath(search_user_res, '$..status')
                            employee_code_count = employee_code_count + employee_code
                            employee_mobile_count = employee_mobile_count + employee_mobile
                            employee_dep_name_count = employee_dep_name_count + employee_dep
                            employee_name_count = employee_name_count + employee_name
                            employee_id_count = employee_id_count + employee_id
                            employee_dep_id_count = employee_dep_id_count + employee_dep_id
                            employee_status_count = employee_status_count + employee_status
            employee_status_count = ["在职" if x == 0 else "离职" for x in employee_status_count]
        # print(employee_code_count, employee_name_count, employee_mobile_count, employee_dep_name_count,
        #         employee_dep_id_count, employee_id_count, employee_status_count)
        return (employee_code_count, employee_name_count, employee_mobile_count, employee_dep_name_count,
                employee_dep_id_count, employee_id_count, employee_status_count)
    def mian_user_search(self):
        company_leaf_departments_id_dict = self.get_department()
        employee_code_count, employee_name_count, employee_mobile_count, employee_dep_name_count, employee_dep_id_count, employee_id_count, employee_status_count\
            = self.get_users(company_leaf_departments_id_dict)
        # 创建DataFrame
        df = pd.DataFrame({
            '工号': employee_code_count,
            '姓名': employee_name_count,
            '手机': employee_mobile_count,
            '部门全称': employee_dep_name_count,
            '部门ID': employee_dep_id_count,
            'user_id': employee_id_count,
            '状态': employee_status_count
        })
        if "uat" in self.Auth_Base_URL or "fat" in self.Auth_Base_URL:
            # 写入 Excel 文件并保留表头
            with pd.ExcelWriter(auth_users_test_dir, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)
            auth_users_test_name = auth_users_test_dir.split("\\")[-1]
            print(f"数据已成功追加到Excel文件：{auth_users_test_name}中。")

        else:
            # 写入 Excel 文件并保留表头
            with pd.ExcelWriter(auth_users_formal_dir, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)
            auth_users_formal_name = auth_users_formal_dir.split("\\")[-1]
            print(f"数据已成功追加到Excel文件：{auth_users_formal_name}中。")



if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin(system_name="auth", environment="pro").soo_login()
    SOOUsers(target_rss=target_rss, environment="pro").mian_user_search()
