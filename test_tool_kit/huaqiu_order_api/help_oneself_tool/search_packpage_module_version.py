import subprocess

import requests


class SearchPackPageModuleVersion:
    # 查看包装页面模块版本
    def __init__(self, module_name=None):
        self.rss = requests.Session()
        self.module_name = module_name

    def search_packpage_module_version(self):
        result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE, text=True)
        packages = result.stdout
        # print(packages)
        for line in packages.splitlines():
            # 转成小写
            line_l = line.lower()
            # 进行切片获取包名
            split_line_package = line_l.split()
            split_line_package_name = split_line_package[0]
            if self.module_name == split_line_package_name:
                print(line)
if __name__ == '__main__':
    module_name = "selenium"
    SearchPackPageModuleVersion(module_name).search_packpage_module_version()