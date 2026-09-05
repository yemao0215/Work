#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SEO 标准化全自动检测脚本
# 适配百度/谷歌SEO标准化规范，可批量/单页检测

import requests
from bs4 import BeautifulSoup
import time
import re

from urllib3.exceptions import InsecureRequestWarning

# 关闭请求警告


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SEOStdDetect:
    def __init__(self, url):
        self.url = url.strip()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.soup = None
        self.response = None
        self.result = {
            "网站链接": self.url,
            "检测状态": "",
            "SEO合规项": [],
            "优化建议": []
        }

    def get_page_html(self):
        """获取网页源码"""
        try:
            self.response = requests.get(
                self.url, headers=self.headers, timeout=10, verify=False
            )
            self.response.encoding = "utf-8"
            self.soup = BeautifulSoup(self.response.text, "lxml")
            self.result["检测状态"] = "检测成功"
            return True
        except Exception as e:
            self.result["检测状态"] = f"页面访问失败：{str(e)}"
            return False

    def check_title(self):
        """1. 检测Title标题 标准：20-60字符，非空、无重复"""
        title = self.soup.find("title")
        if not title or not title.get_text().strip():
            self.result["SEO合规项"].append("❌ Title标题为空（违规）")
            self.result["优化建议"].append("为网页设置唯一、精准的标题，包含核心关键词")
            return
        title_text = title.get_text().strip()
        title_len = len(title_text)
        if 20 <= title_len <= 60:
            self.result["SEO合规项"].append(f"✅ Title合规（长度：{title_len}字）：{title_text}")
        else:
            self.result["SEO合规项"].append(f"❌ Title长度不规范（当前{title_len}字，标准20-60字）")
            self.result["优化建议"].append("调整标题长度至20-60字符，避免过短无权重、过长被搜索引擎截断")

    def check_description(self):
        """2. 检测Meta描述 标准：50-120字符"""
        desc = self.soup.find("meta", attrs={"name": "description"})
        if not desc or not desc.get("content", "").strip():
            self.result["SEO合规项"].append("❌ Meta描述为空（违规）")
            self.result["优化建议"].append("编写原创描述，包含页面核心业务关键词，吸引搜索点击")
            return
        desc_text = desc.get("content").strip()
        desc_len = len(desc_text)
        if 50 <= desc_len <= 120:
            self.result["SEO合规项"].append(f"✅ 描述合规（长度：{desc_len}字）：{desc_text}")
        else:
            self.result["SEO合规项"].append(f"❌ 描述长度不规范（当前{desc_len}字，标准50-120字）")
            self.result["优化建议"].append("调整描述字数至50-120字符，简洁概括页面内容")

    def check_keywords(self):
        """3. 检测关键词"""
        kw = self.soup.find("meta", attrs={"name": "keywords"})
        if not kw or not kw.get("content", "").strip():
            self.result["SEO合规项"].append("⚠️ Keywords关键词未设置（不影响排名，建议补充）")
        else:
            self.result["SEO合规项"].append(f"✅ 关键词已设置：{kw.get('content').strip()}")

    def check_h_tag(self):
        """4. 检测H标签层级：唯一H1，层级依次递减"""
        h1_list = self.soup.find_all("h1")
        h2_list = self.soup.find_all("h2")
        h3_list = self.soup.find_all("h3")

        if len(h1_list) == 0:
            self.result["SEO合规项"].append("❌ 页面无H1标签（严重违规）")
            self.result["优化建议"].append("页面必须设置1个唯一H1标签，定义页面核心主题")
        elif len(h1_list) > 1:
            self.result["SEO合规项"].append(f"❌ H1标签数量异常（当前{len(h1_list)}个，仅限1个）")
            self.result["优化建议"].append("保留唯一H1标签，其余改为H2/H3，保证层级唯一")
        else:
            self.result["SEO合规项"].append("✅ H1标签合规（唯一）")

        if not h2_list and not h3_list:
            self.result["SEO合规项"].append("⚠️ 页面无H2/H3层级标签，内容层级不清晰")
            self.result["优化建议"].append("为页面内容添加H2、H3分层标签，提升页面结构化权重")

    def check_img_alt(self):
        """5. 检测图片ALT属性"""
        img_list = self.soup.find_all("img")
        if not img_list:
            self.result["SEO合规项"].append("✅ 页面无图片，无需检测ALT属性")
            return
        error_img = 0
        for img in img_list:
            if not img.get("alt", "").strip():
                error_img += 1
        if error_img > 0:
            self.result["SEO合规项"].append(f"❌ 存在{error_img}张图片无ALT属性（违规）")
            self.result["优化建议"].append("所有图片必须添加ALT说明，包含场景关键词，提升图片收录")
        else:
            self.result["SEO合规项"].append(f"✅ 全部{len(img_list)}张图片ALT属性合规")

    def check_link(self):
        """6. 检测空链接、无效链接"""
        a_list = self.soup.find_all("a")
        null_link = 0
        for a in a_list:
            href = a.get("href", "").strip()
            if not href or href == "#" or href == "javascript:;":
                null_link += 1
        if null_link > 0:
            self.result["SEO合规项"].append(f"❌ 存在{null_link}个空/无效锚链接")
            self.result["优化建议"].append("删除无效空链接，或替换为有效内链/外链，避免权重流失")
        else:
            self.result["SEO合规项"].append(f"✅ 全部{len(a_list)}个链接合规")

    def check_viewport(self):
        """7. 检测移动端适配viewport"""
        viewport = self.soup.find("meta", attrs={"name": "viewport"})
        if viewport and "width=device-width" in viewport.get("content", ""):
            self.result["SEO合规项"].append("✅ 移动端viewport适配合规")
        else:
            self.result["SEO合规项"].append("❌ 未配置移动端适配（无法自适应手机端）")
            self.result["优化建议"].append("添加标准viewport适配代码，保障移动端SEO排名")

    def check_encoding(self):
        """8. 检测网页编码UTF-8"""
        encode_meta = self.soup.find("meta", charset=True)
        if encode_meta and encode_meta.get("charset", "").upper() == "UTF-8":
            self.result["SEO合规项"].append("✅ 网页编码UTF-8合规")
        else:
            self.result["SEO合规项"].append("❌ 网页非UTF-8编码，易出现乱码、收录异常")
            self.result["优化建议"].append("统一设置网页编码为UTF-8")

    def check_https(self):
        """9. 检测HTTPS协议"""
        if self.url.startswith("https"):
            self.result["SEO合规项"].append("✅ HTTPS安全协议合规")
        else:
            self.result["SEO合规项"].append("❌ 网站为HTTP不安全协议，影响搜索引擎评级")
            self.result["优化建议"].append("部署SSL证书，全站升级HTTPS并做301重定向")

    def check_load_speed(self):
        """10. 检测网页加载速度"""
        start_time = time.time()
        res = requests.get(self.url, headers=self.headers, timeout=10, verify=False)
        load_time = round(time.time() - start_time, 2)
        if load_time < 2:
            self.result["SEO合规项"].append(f"✅ 页面加载速度优秀（{load_time}s）")
        elif load_time < 4:
            self.result["SEO合规项"].append(f"⚠️ 页面加载速度一般（{load_time}s，建议<2s）")
            self.result["优化建议"].append("压缩图片、精简代码、开启缓存，优化页面加载速度")
        else:
            self.result["SEO合规项"].append(f"❌ 页面加载过慢（{load_time}s，严重影响SEO排名）")
            self.result["优化建议"].append("紧急优化：CDN加速、静态资源压缩、减少冗余代码")

    def run_all_check(self):
        """执行全部检测项"""
        if not self.get_page_html():
            return self.result

        # 逐条执行检测
        self.check_title()
        self.check_description()
        self.check_keywords()
        self.check_h_tag()
        self.check_img_alt()
        self.check_link()
        self.check_viewport()
        self.check_encoding()
        self.check_https()
        self.check_load_speed()

        return self.result


# ==================== 调用运行 ====================
if __name__ == "__main__":
    print("===== SEO标准化全自动检测工具 =====")
    target_url = input("请输入需要检测的网址：")
    seo = SEOStdDetect(target_url)
    res = seo.run_all_check()

    # 格式化输出结果
    print("\n【检测结果汇总】")
    print(f"检测网址：{res['网站链接']}")
    print(f"检测状态：{res['检测状态']}")
    print("\n【SEO合规详情】")
    for item in res["SEO合规项"]:
        print(item)
    print("\n【优化建议】")
    if res["优化建议"]:
        for sug in res["优化建议"]:
            print(f"- {sug}")
    else:
        print("- 所有SEO项均符合标准化规范，无需优化")
