#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 华秋商城搜索页专属SEO标准化审计脚本（适配审计文档V0.8）
# 校验规则完全对齐《01-SEO现状审计与改版策略.md》
import re
import json
import time
from urllib.parse import urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup
from jsonschema import validate, ValidationError

# 关闭https警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Breadcrumb结构化数据校验模板
BREADCRUMB_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "@context": {"type": "string", "const": "https://schema.org"},
        "@type": {"type": "string", "const": "BreadcrumbList"},
        "itemListElement": {"type": "array"}
    },
    "required": ["@context", "@type", "itemListElement"]
}

class HuaQiuSearchSEOAudit:
    def __init__(self, url):
        self.raw_url = url.strip()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Baiduspider/2.0",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        self.mobile_ua = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        }
        self.soup = None
        self.response = None
        self.status_code = 0
        self.url_parse = urlparse(self.raw_url)
        self.query_params = parse_qs(self.url_parse.query)
        self.path = self.url_parse.path
        # 审计结果存储
        self.audit_result = {
            "检测网址": self.raw_url,
            "页面类型": self._judge_page_type(),
            "HTTP状态码": 0,
            "检测总状态": "",
            "P0阻塞上线问题": [],
            "P1本期优化问题": [],
            "P2低风险兼容项": [],
            "合规通过项": [],
            "页面基础元数据": {},
            "商品渲染校验": {},
            "结构化数据": {},
            "页面URL参数": self.query_params
        }

    def _judge_page_type(self):
        """根据URL规则判定页面类型（对齐文档6.2页面矩阵）"""
        path_rule = re.compile(r"^/search/.*\.html$")
        is_main_search = path_rule.match(self.path)
        has_filter = any(k in ["brand", "category", "package", "supplier"] for k in self.query_params.keys())
        has_sort = "sort" in self.query_params
        has_page = int(self.query_params.get("page", ["1"])[0]) if "page" in self.query_params else 1
        has_track = any(k in ["hq_source", "spm"] for k in self.query_params.keys())

        if not is_main_search:
            return "非搜索页"
        if has_filter:
            return "筛选页-noindex"
        if has_sort:
            return "排序页-noindex"
        if has_page and has_page > 1:
            return "分页页-noindex"
        if has_track:
            return "带跟踪参数页"
        return "精确型号主索引页-index"

    def fetch_html(self):
        """拉取页面HTML，记录状态码"""
        try:
            self.response = requests.get(
                self.raw_url, headers=self.headers, timeout=12, verify=False
            )
            self.status_code = self.response.status_code
            self.audit_result["HTTP状态码"] = self.status_code
            self.response.encoding = "utf-8"
            self.soup = BeautifulSoup(self.response.text, "lxml")
            self.audit_result["检测总状态"] = "页面拉取成功"
            return True
        except Exception as e:
            self.audit_result["检测总状态"] = f"页面访问失败：{str(e)}"
            return False

    def check_http_status(self):
        """P0校验：页面状态码规则（文档6.2矩阵）"""
        page_type = self.audit_result["页面类型"]
        if page_type in ["精确型号主索引页-index", "筛选页-noindex", "排序页-noindex", "分页页-noindex", "带跟踪参数页"]:
            if self.status_code != 200:
                self.audit_result["P0阻塞上线问题"].append(
                    f"【状态码违规】{page_type}必须返回HTTP 200，当前{self.status_code}"
                )
            else:
                self.audit_result["合规通过项"].append(f"✅ 状态码合规：200")
        # 无结果/越界页面校验（需人工配合测试，此处仅标记检测项）
        elif self.status_code == 404:
            self.audit_result["合规通过项"].append("✅ 无结果/无效分页返回404，符合规范")
        else:
            self.audit_result["P0阻塞上线问题"].append(f"【状态码异常】非预期状态码{self.status_code}")

    def check_html_lang(self):
        """P0：强制校验 <html lang="zh-CN">"""
        html_tag = self.soup.find("html")
        if not html_tag or html_tag.get("lang") != "zh-CN":
            self.audit_result["P0阻塞上线问题"].append("【HTML语义缺失】未设置<html lang='zh-CN'>，P0阻塞")
        else:
            self.audit_result["合规通过项"].append("✅ html lang=zh-CN 设置合规")

    def check_viewport(self):
        """P0：viewport禁止禁止缩放，必须允许缩放"""
        vp_meta = self.soup.find("meta", attrs={"name": "viewport"})
        if not vp_meta:
            self.audit_result["P0阻塞上线问题"].append("【移动端适配缺失】无viewport meta标签，P0阻塞")
            return
        vp_content = vp_meta.get("content", "")
        if "user-scalable=no" in vp_content or "maximum-scale=1" in vp_content:
            self.audit_result["P0阻塞上线问题"].append(f"【viewport违规】禁止缩放配置：{vp_content}，需移除user-scalable=no")
        else:
            self.audit_result["合规通过项"].append("✅ viewport支持缩放，移动端适配合规")

    def check_title_desc(self):
        """P0：Title/Description 模板校验，禁止型号重复堆叠下划线"""
        # Title校验
        title_tag = self.soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else ""
        self.audit_result["页面基础元数据"]["title"] = title_text
        page_type = self.audit_result["页面类型"]

        if not title_text:
            self.audit_result["P0阻塞上线问题"].append("【Title缺失】页面无Title标签，P0阻塞")
        else:
            # 检测下划线拼接、型号重复3次以上风险
            model_list = re.findall(r"[A-Z0-9]+[_A-Z0-9]+", title_text)
            under_line_count = title_text.count("_")
            if under_line_count >= 2:
                self.audit_result["P0阻塞上线问题"].append(f"【Title格式违规】使用下划线堆叠文案：{title_text}，需改用推荐模板")
            if len(model_list) >= 3:
                self.audit_result["P0阻塞上线问题"].append(f"【Title重复风险】型号机械重复{len(model_list)}次，降低CTR")
            if page_type == "精确型号主索引页-index" and "价格、库存、参数与数据手册" not in title_text:
                self.audit_result["P1本期优化问题"].append(f"【Title模板不标准】未使用官方推荐型号页Title模板")
            self.audit_result["合规通过项"].append(f"✅ Title存在：{title_text[:60]}...")

        # Description校验
        desc_meta = self.soup.find("meta", {"name": "description"})
        desc_text = desc_meta.get("content", "").strip() if desc_meta else ""
        self.audit_result["页面基础元数据"]["description"] = desc_text
        if not desc_text:
            self.audit_result["P0阻塞上线问题"].append("【Description缺失】无meta description，P0阻塞")
        else:
            model_dup = len(re.findall(r"[A-Z0-9]+[_A-Z0-9]+", desc_text))
            if model_dup >= 3:
                self.audit_result["P1本期优化问题"].append(f"【Description型号重复过多】共重复{model_dup}次，文案机械")
            self.audit_result["合规通过项"].append(f"✅ Description已配置")

    def check_meta_robots(self):
        """P0：Meta Robots唯一、无冲突，匹配页面类型索引规则"""
        robots_meta = self.soup.find("meta", {"name": "robots"})
        page_type = self.audit_result["页面类型"]
        if not robots_meta:
            self.audit_result["P0阻塞上线问题"].append("【Robots缺失】无meta robots标签，无法精细控制收录，P0阻塞")
            return
        robots_content = robots_meta.get("content", "").strip()
        self.audit_result["页面基础元数据"]["robots"] = robots_content
        # 校验冲突指令
        if "index" in robots_content and "noindex" in robots_content:
            self.audit_result["P0阻塞上线问题"].append(f"【Robots冲突】同时包含index/noindex：{robots_content}，P0阻塞")
        # 分页面类型校验标准robots值
        expect_robots = ""
        if page_type == "精确型号主索引页-index":
            expect_robots = "index,follow"
        else:
            expect_robots = "noindex,follow"
        if robots_content != expect_robots:
            self.audit_result["P0阻塞上线问题"].append(
                f"【Robots不匹配页面类型】页面类型{page_type}预期{expect_robots}，实际{robots_content}"
            )
        else:
            self.audit_result["合规通过项"].append(f"✅ Robots指令合规：{robots_content}")

    def check_canonical_alternate(self):
        """P0：Canonical规范 + PC/M alternate移动端适配校验"""
        canonical_link = self.soup.find("link", {"rel": "canonical"})
        alternate_link = self.soup.find("link", {"rel": "alternate"})
        page_type = self.audit_result["页面类型"]
        self.audit_result["页面基础元数据"]["canonical"] = canonical_link.get("href", "") if canonical_link else ""
        # Canonical基础校验
        if not canonical_link:
            self.audit_result["P0阻塞上线问题"].append("【Canonical缺失】无规范链接标签，P0阻塞")
        else:
            can_url = canonical_link.get("href")
            can_parse = urlparse(can_url)
            # 筛选/排序/跟踪页canonical必须指向纯净主搜索页
            if page_type in ["筛选页-noindex", "排序页-noindex", "带跟踪参数页"]:
                if "?" in can_url or re.search(r"hq_source|spm|sort|brand", can_url):
                    self.audit_result["P0阻塞上线问题"].append(f"【Canonical净化失败】筛选/排序页canonical携带参数：{can_url}")
                else:
                    self.audit_result["合规通过项"].append("✅ 筛选/排序页Canonical已去除参数指向主页面")
            # 主索引页/分页自引用
            elif page_type in ["精确型号主索引页-index", "分页页-noindex"]:
                if unquote(can_parse.path) != unquote(self.path):
                    self.audit_result["P0阻塞上线问题"].append(f"【Canonical不自引用】主页面应指向自身，当前{can_url}")
                else:
                    self.audit_result["合规通过项"].append("✅ Canonical自引用合规")
        # PC/M alternate校验 P0
        if not alternate_link or "media=only screen and (max-width: 640px)" not in str(alternate_link):
            self.audit_result["P0阻塞上线问题"].append("【移动端alternate缺失】未配置M端对应链接，PC/M关系断裂")
        else:
            self.audit_result["合规通过项"].append("✅ PC页面alternate移动端链接配置完成")

    def check_h_tags_semantic(self):
        """P0：H标签语义强校验：唯一H1、禁止导航包裹H2、分组H2规范"""
        h1_list = self.soup.find_all("h1")
        h2_list = self.soup.find_all("h2")
        # H1唯一校验 P0
        if len(h1_list) == 0:
            self.audit_result["P0阻塞上线问题"].append("【H1缺失】页面无主H1标题，语义失效，P0阻塞")
        elif len(h1_list) > 1:
            self.audit_result["P0阻塞上线问题"].append(f"【H1数量违规】共{len(h1_list)}个H1，仅允许1个")
        else:
            h1_text = h1_list[0].get_text(strip=True)
            if h1_text.lower() in ["logo", "首页"]:
                self.audit_result["P0阻塞上线问题"].append(f"【H1语义错误】Logo占用唯一H1：{h1_text}")
            else:
                self.audit_result["合规通过项"].append(f"✅ 唯一H1合规：{h1_text[:40]}")
        # H2禁止包裹导航 P0
        nav_wrap_h2 = False
        for h2 in h2_list:
            if h2.find("nav") or h2.find("ul", class_=re.compile(r"nav|menu")):
                nav_wrap_h2 = True
                break
        if nav_wrap_h2:
            self.audit_result["P0阻塞上线问题"].append("【H2语义违规】H2标签包裹导航菜单，破坏页面层级")
        else:
            self.audit_result["合规通过项"].append("✅ H2未包裹导航，语义合规")
        # H2分组提示 P1
        h2_texts = [h.get_text(strip=True) for h in h2_list]
        if "华秋自营" not in h2_texts and "合作库存" not in h2_texts:
            self.audit_result["P1本期优化问题"].append("【H2分组缺失】未使用H2区分自营/合作库存商品分组")

    def check_goods_render(self):
        """P0：校验服务端是否输出首屏商品（区分Vue异步模板风险）"""
        soup_text = str(self.soup)
        self.audit_result["商品渲染校验"]["原始HTML含Vue模板"] = bool(re.search(r"v-for|v-if|{{.*}}", soup_text))
        # 检测自营商品关键字段
        has_model = re.search(r"型号[:：]\w+", soup_text)
        has_price = re.search(r"阶梯价格|¥\d+", soup_text)
        has_stock = re.search(r"库存|现货", soup_text)
        has_item_link = re.search(r"href.*item\.hqchip\.com", soup_text)
        self.audit_result["商品渲染校验"]["首屏存在型号"] = bool(has_model)
        self.audit_result["商品渲染校验"]["首屏存在价格"] = bool(has_price)
        self.audit_result["商品渲染校验"]["首屏存在库存"] = bool(has_stock)
        self.audit_result["商品渲染校验"]["首屏商品详情链接"] = bool(has_item_link)

        # P0阻塞：主索引页无商品基础数据
        page_type = self.audit_result["页面类型"]
        if page_type == "精确型号主索引页-index":
            if not (has_model and has_price and has_item_link):
                self.audit_result["P0阻塞上线问题"].append("【渲染违规】服务端HTML未输出首屏商品型号/价格/详情链接，纯CSR无法收录")
            else:
                self.audit_result["合规通过项"].append("✅ 服务端HTML包含首屏自营商品核心数据")
        # Vue异步标记风险 P1
        if re.search(r"v-for|{{item\.goodsDesc}}", soup_text):
            self.audit_result["P1本期优化问题"].append("【异步渲染风险】更多渠道商品依赖Vue客户端渲染，爬虫无法抓取")

    def check_img_alt_rule(self):
        """P0：商品图片原生img、必填alt、禁止仅data-src"""
        all_img = self.soup.find_all("img")
        error_img = 0
        data_src_only = 0
        for img in all_img:
            src = img.get("src", "")
            data_src = img.get("data-src", "")
            alt = img.get("alt", "").strip()
            # 仅data-src无原生src
            if not src and data_src:
                data_src_only += 1
            # alt为空违规
            if not alt:
                error_img += 1
        if data_src_only > 0:
            self.audit_result["P0阻塞上线问题"].append(f"【图片渲染违规】{data_src_only}张图片仅使用data-src，无原生src爬虫不可见")
        if error_img > 0:
            self.audit_result["P0阻塞上线问题"].append(f"【图片alt缺失】{error_img}张商品图片无alt替代文本")
        if data_src_only == 0 and error_img == 0 and len(all_img) > 0:
            self.audit_result["合规通过项"].append(f"✅ 全部{len(all_img)}张图片原生src+alt完整")

    def check_anchor_link(self):
        """P0：商品/分页/手册必须原生a href，过滤无效空链接"""
        a_tags = self.soup.find_all("a")
        invalid_link = 0
        page_link_ok = False
        goods_link_ok = False
        for a in a_tags:
            href = a.get("href", "").strip()
            # 无效链接 # / javascript
            if not href or href == "#" or href.startswith("javascript"):
                invalid_link += 1
            # 分页链接存在
            if re.search(r"page=\d+", href):
                page_link_ok = True
            # 商品详情链接
            if "item.hqchip.com" in href:
                goods_link_ok = True
        if invalid_link > 10:
            self.audit_result["P1本期优化问题"].append(f"【无效链接过多】页面存在{invalid_link}个#/js空锚链接")
        page_type = self.audit_result["页面类型"]
        if page_type != "非搜索页":
            if not goods_link_ok:
                self.audit_result["P0阻塞上线问题"].append("【链接违规】无原生商品详情<a href>链接，爬虫无法抓取单品")
            else:
                self.audit_result["合规通过项"].append("✅ 商品详情使用原生a href链接")
            if not page_link_ok and "page" in self.query_params:
                self.audit_result["P0阻塞上线问题"].append("【分页违规】分页无原生可抓取<a href>，无法收录后续页面")

    def check_breadcrumb_jsonld(self):
        """P1：仅校验必做BreadcrumbList结构化数据"""
        json_ld_list = self.soup.find_all("script", type="application/ld+json")
        breadcrumb_valid = False
        for script in json_ld_list:
            try:
                json_data = json.loads(script.get_text(strip=True))
                if isinstance(json_data, dict) and json_data.get("@type") == "BreadcrumbList":
                    validate(instance=json_data, schema=BREADCRUMB_SCHEMA)
                    breadcrumb_valid = True
                    self.audit_result["结构化数据"]["BreadcrumbList"] = "校验通过"
                    break
            except (json.JSONDecodeError, ValidationError):
                continue
        if not breadcrumb_valid:
            self.audit_result["P1本期优化问题"].append("【结构化缺失】未部署合规BreadcrumbList面包屑JSON-LD")
        else:
            self.audit_result["合规通过项"].append("✅ BreadcrumbList结构化数据校验通过")

    def check_mixed_http(self):
        """P1：检测页面内http混合资源"""
        html_str = str(self.soup)
        http_res = re.findall(r"http://[^\s\"']+", html_str)
        unique_http = list(set(http_res))
        if len(unique_http) > 0:
            self.audit_result["P1本期优化问题"].append(f"【混合内容风险】页面存在http资源链接：{unique_http[:3]}")
        else:
            self.audit_result["合规通过项"].append("✅ 页面无http混合资源，全站HTTPS")

    def run_full_audit(self):
        """执行全套审计"""
        if not self.fetch_html():
            return self.audit_result
        # 按优先级执行校验
        self.check_http_status()
        self.check_html_lang()
        self.check_viewport()
        self.check_title_desc()
        self.check_meta_robots()
        self.check_canonical_alternate()
        self.check_h_tags_semantic()
        self.check_goods_render()
        self.check_img_alt_rule()
        self.check_anchor_link()
        self.check_breadcrumb_jsonld()
        self.check_mixed_http()
        return self.audit_result

    def print_report(self):
        """格式化输出审计报告"""
        res = self.audit_result
        print("=" * 80)
        print("华秋商城搜索页SEO标准化审计报告（适配文档V0.8）")
        print("=" * 80)
        print(f"检测URL：{res['检测网址']}")
        print(f"页面分类：{res['页面类型']} | HTTP状态码：{res['HTTP状态码']}")
        print(f"页面拉取状态：{res['检测总状态']}\n")

        print("【🔴 P0 阻塞上线问题（必须修复才能发布）】")
        if res["P0阻塞上线问题"]:
            for idx, msg in enumerate(res["P0阻塞上线问题"], 1):
                print(f"{idx}. {msg}")
        else:
            print("无P0阻塞问题，基础SEO合规")
        print("\n【🟡 P1 本期必须优化项】")
        if res["P1本期优化问题"]:
            for idx, msg in enumerate(res["P1本期优化问题"], 1):
                print(f"{idx}. {msg}")
        else:
            print("无P1优化项")
        print("\n【🟢 合规通过项】")
        for item in res["合规通过项"]:
            print(f"- {item}")

        print("\n【页面核心元数据】")
        meta = res["页面基础元数据"]
        for k, v in meta.items():
            print(f"{k}: {v}")

        print("\n【商品渲染检测结果】")
        render = res["商品渲染校验"]
        for k, v in render.items():
            print(f"{k}: {v}")

        print("\n【结构化数据校验】")
        struct = res["结构化数据"]
        for k, v in struct.items():
            print(f"{k}: {v}")
        print("=" * 80)


# 程序入口
if __name__ == "__main__":
    print("===== 华秋商城搜索页专属SEO审计工具 =====")
    print("校验规则完全对齐《01-SEO现状审计与改版策略V0.8》")
    target_url = input("请输入待审计搜索页面URL：")
    audit = HuaQiuSearchSEOAudit(target_url)
    audit.run_full_audit()
    audit.print_report()