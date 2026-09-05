import json

import requests
import yaml

from huaqiu_order_api.HQSTENCIL.HTYSMT.login import StencilHtysmt
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class HTYSMTStencilOrderCancellation:
    def __init__(self,rss, order_sn=None):
        self.order_sn = order_sn
        self.rss = rss
        self.headers = {"Content-Type": "application/json; charset=utf-8"}
        self.form_headers = {"Content-Type": "application/x-www-form-urlencoded",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.data_headers = {"Content-Type": "multipart/form-data",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HTYSMT_URL = data['HTYSMT_URL']
        token = getattr(Data, "htysmt_token")
        # userId = getattr(Data, "htysmt_userId", '')
        self.headers["Authorization"] = "Bearer " + token
    def extract_menu_hierarchy(self, data, parent_id=0, level=0):
        """
        递归提取菜单层级关系
        返回包含所有节点层级信息的列表
        """
        result = []

        for item in data:
            # 提取当前节点的关键信息
            node_info = {
                'id': item.get('id'),
                'parent_id': parent_id,
                'title': item.get('title'),
                'name': item.get('name'),
                'path': item.get('path', ''),
                'component': item.get('component', ''),
                'formId': item.get('formId', 0),
                'level': level,
                'type': item.get('meta', {}).get('type', 0),  # 1: 目录, 2: 菜单
                'icon': item.get('meta', {}).get('icon', ''),
                'hideMenu': item.get('meta', {}).get('hideMenu', False),
                'orderNo': item.get('meta', {}).get('orderNo', 0),
                'children_ids': []  # 暂时为空，后面填充
            }

            # 处理子节点
            children = item.get('children', [])
            if children:
                # 递归提取子节点信息
                child_results = self.extract_menu_hierarchy(children, item.get('id'), level + 1)
                # 收集子节点ID
                node_info['children_ids'] = [child['id'] for child in child_results]
                # 合并子节点结果
                result.extend(child_results)

            result.append(node_info)

        return result
    def build_hierarchy_dict(self, data):
        """
        构建层级关系字典
        返回两个字典：
        1. 按ID索引的节点信息
        2. 树形结构（嵌套的层级关系）
        """
        # 提取所有节点（扁平化）
        all_nodes = self.extract_menu_hierarchy(data)

        # 构建ID索引字典
        node_dict = {node['id']: node for node in all_nodes}

        # 构建树形结构
        tree = []
        for node in all_nodes:
            if node['parent_id'] == 0:
                # 顶级节点
                tree.append(node)

        # 为每个节点添加 children 引用（方便查看树形结构）
        for node in all_nodes:
            node['children'] = []
            for child_id in node['children_ids']:
                if child_id in node_dict:
                    node['children'].append(node_dict[child_id])

        return {
            'node_dict': node_dict,  # 按ID索引的所有节点
            'tree': tree,  # 树形结构（顶级节点开始）
            'all_nodes': all_nodes  # 扁平化列表
        }
    def stencil_jig_module(self):
        """钢网治具模块信息"""
        get_user_role_menu_url = "{}/api/getUserRoleMenu".format(self.HTYSMT_URL)
        get_user_role_menu_res = self.rss.get(url=get_user_role_menu_url, headers=self.headers).json()
        hierarchy = self.build_hierarchy_dict(get_user_role_menu_res["data"])
        # print(hierarchy)
        export_data = []
        for node in hierarchy['all_nodes']:
            export_data.append({
                'id': node['id'],
                'parent_id': node['parent_id'],
                'title': node['title'],
                'path': node['path'],
                'component': node['component'],
                'formId': node['formId'],
                'level': node['level'],
                'children_ids': node['children_ids']
            })
        print(json.dumps(export_data, indent=2, ensure_ascii=False))  # 只打印前5个
        # 1. 查看所有节点（扁平化列表）
        # print("=== 所有节点（扁平化）===")
        # for node in hierarchy['all_nodes']:
        #     print(f"ID: {node['id']}, 父ID: {node['parent_id']}, Title: {node['title']}, Level: {node['level']}")
        #
        # print("\n" + "=" * 80 + "\n")


    def stencil_order_search(self):
        stencil_order_search_url = "{}"

if __name__ == '__main__':
    rss = StencilHtysmt().login()
    HTYSMTStencilOrderCancellation(rss=rss).stencil_jig_module()