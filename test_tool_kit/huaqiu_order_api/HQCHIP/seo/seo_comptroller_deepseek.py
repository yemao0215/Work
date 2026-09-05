#!/usr/bin/env python3
"""
华秋商城 SEO 标准化检测脚本
基于 SEO 现状审计与改版策略文档 (V0.8)
符合华秋商城搜索结果页 SEO 审计标准

使用方式:
    python seo_audit.py --url https://www.hqchip.com/search/MPXHZ6400AC6T1.html
    python seo_audit.py --url https://www.hqchip.com/search/STM32.html --output report.html
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown


@dataclass
class AuditResult:
    """审计结果数据类"""
    check_name: str
    status: str  # PASS, FAIL, WARN, INFO
    message: str
    priority: str  # P0, P1, P2
    details: Optional[Dict] = None
    suggestion: Optional[str] = None


@dataclass
class PageAudit:
    """页面审计汇总"""
    url: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    results: List[AuditResult] = field(default_factory=list)
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    total_score: int = 0
    max_score: int = 0

    def add_result(self, result: AuditResult):
        self.results.append(result)
        if result.status == "PASS":
            self.total_score += 1
        self.max_score += 1

    def get_summary(self) -> Dict:
        """获取审计摘要"""
        stats = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
        priority_counts = {"P0": {"PASS": 0, "FAIL": 0, "WARN": 0},
                           "P1": {"PASS": 0, "FAIL": 0, "WARN": 0},
                           "P2": {"PASS": 0, "FAIL": 0, "WARN": 0}}

        for r in self.results:
            stats[r.status] = stats.get(r.status, 0) + 1
            if r.priority in priority_counts:
                priority_counts[r.priority][r.status] = priority_counts[r.priority].get(r.status, 0) + 1

        return {
            "stats": stats,
            "priority_counts": priority_counts,
            "score": f"{self.total_score}/{self.max_score}",
            "pass_rate": f"{(self.total_score / self.max_score * 100):.1f}%" if self.max_score > 0 else "0%"
        }


class SEOAuditor:
    """SEO审计器"""

    # 页面类型与收录矩阵
    PAGE_TYPES = {
        "exact_model": "有有效结果且通过质量门槛的精确型号主页面",
        "broad_search": "普通宽泛搜索词页面",
        "filter": "单项/多项筛选页面",
        "sort": "排序页面",
        "tracking": "跟踪参数页面",
        "pagination": "第2页及以后",
        "no_result": "无有效结果的搜索页",
        "invalid": "无效/越界筛选或分页"
    }

    def __init__(self, url: str, timeout: int = 30, user_agent: str = None):
        self.url = url
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (compatible; SEOAuditBot/1.0; +https://www.hqchip.com)"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.soup = None
        self.response = None
        self.parsed_url = None

    def fetch(self) -> bool:
        """获取页面内容"""
        try:
            self.response = self.session.get(self.url, timeout=self.timeout)
            self.status_code = self.response.status_code
            self.content_type = self.response.headers.get("Content-Type", "")

            if "text/html" in self.content_type:
                self.soup = BeautifulSoup(self.response.text, "html.parser")
                self.parsed_url = urlparse(self.url)
                return True
            return False
        except Exception as e:
            print(f"获取页面失败: {e}")
            return False

    def detect_page_type(self) -> Tuple[str, str]:
        """检测页面类型"""
        # 从URL和内容检测页面类型
        query = parse_qs(self.parsed_url.query)

        # 检查是否有筛选参数
        has_filter = any(p in query for p in ["brand", "category", "package", "supplier"])
        has_sort = "sort" in query
        has_tracking = any(p in query for p in ["hq_source", "spm", "utm_"])
        has_page = "page" in query and query.get("page", ["1"])[0] != "1"

        # 检查是否有搜索结果
        has_results = self._check_has_results()

        # 检测搜索词是否是型号
        keyword = self._extract_keyword()
        is_exact_model = self._is_exact_model(keyword) if keyword else False

        # 综合判断页面类型
        if not has_results:
            return "no_result", "无有效结果的搜索页"

        if has_tracking:
            return "tracking", "跟踪参数页面"

        if has_filter and has_sort:
            return "filter", "多项筛选页面"

        if has_filter:
            return "filter", "筛选页面"

        if has_sort:
            return "sort", "排序页面"

        if has_page:
            return "pagination", "分页页面"

        if is_exact_model and has_results:
            return "exact_model", "精确型号主页面"

        return "broad_search", "普通宽泛搜索词页面"

    def _check_has_results(self) -> bool:
        """检查页面是否有有效搜索结果"""
        if not self.soup:
            return False

        # 检查是否包含商品卡片
        product_selectors = [".goods-item", ".product-item", ".search-item", "[class*='product']", "[class*='goods']"]
        for selector in product_selectors:
            if self.soup.select(selector):
                return True

        # 检查是否有"暂无结果"等提示
        no_result_patterns = ["暂无", "没有找到", "未找到", "0条", "没有结果", "not found"]
        text = self.soup.get_text()
        for pattern in no_result_patterns:
            if pattern in text:
                return False

        return True

    def _extract_keyword(self) -> Optional[str]:
        """从URL提取搜索关键词"""
        # 从URL路径提取: /search/{keyword}.html
        path = self.parsed_url.path
        match = re.search(r'/search/(.+?)\.html', path)
        if match:
            keyword = match.group(1)
            # 尝试解码URL编码
            try:
                from urllib.parse import unquote
                keyword = unquote(keyword)
            except:
                pass
            return keyword

        # 从查询参数提取
        query = parse_qs(self.parsed_url.query)
        if "q" in query:
            return query["q"][0]
        if "keyword" in query:
            return query["keyword"][0]
        if "k" in query:
            return query["k"][0]

        return None

    def _is_exact_model(self, keyword: str) -> bool:
        """判断是否为精确型号"""
        # 型号特征：字母数字组合，可能包含特殊字符
        # 常见电子元器件型号特征
        model_patterns = [
            r'^[A-Z]{1,5}\d+[A-Z0-9]*',  # 如: MPXHZ6400AC6T1
            r'^[A-Z]{1,3}\d{4,}',  # 如: STM32F103
            r'^[A-Z]{1,5}-\d+',  # 如: LM358-N
            r'^[A-Z0-9]{6,}$',  # 6位以上字母数字组合
        ]

        # 排除明显的宽泛词
        broad_patterns = ["芯片", "集成电路", "元件", "电子", "半导体", "价格", "库存", "采购"]

        keyword_upper = keyword.upper()
        for pattern in broad_patterns:
            if pattern in keyword:
                return False

        for pattern in model_patterns:
            if re.match(pattern, keyword_upper):
                return True

        return False

    def audit_html_lang(self) -> AuditResult:
        """检查HTML语言声明"""
        if not self.soup:
            return AuditResult("HTML语言声明", "FAIL", "无法获取页面内容", "P1")

        html_tag = self.soup.find("html")
        if html_tag and html_tag.get("lang"):
            lang = html_tag.get("lang")
            if lang == "zh-CN":
                return AuditResult("HTML语言声明", "PASS", f"已声明语言: {lang}", "P1")
            else:
                return AuditResult("HTML语言声明", "WARN", f"语言声明为: {lang}，推荐使用: zh-CN", "P1")
        else:
            return AuditResult("HTML语言声明", "FAIL", "未声明语言，缺少语义和辅助技术信息", "P1")

    def audit_title(self) -> AuditResult:
        """检查Title"""
        if not self.soup:
            return AuditResult("Title", "FAIL", "无法获取页面内容", "P0")

        title_tag = self.soup.find("title")
        if not title_tag or not title_tag.string:
            return AuditResult("Title", "FAIL", "缺少Title标签", "P0")

        title = title_tag.string.strip()
        issues = []

        # 检查长度
        if len(title) < 10:
            issues.append("标题过短")
        elif len(title) > 70:
            issues.append("标题过长，可能在搜索结果中被截断")

        # 检查是否重复型号
        keyword = self._extract_keyword()
        if keyword and title.count(keyword) > 1:
            issues.append(f"型号 '{keyword}' 重复出现 {title.count(keyword)} 次")

        # 检查是否使用下划线堆叠
        if "_" in title:
            issues.append("标题使用下划线分隔，可能影响可读性")

        # 检查是否包含"华秋商城"
        if "华秋" not in title and "华秋商城" not in title:
            issues.append("标题未包含品牌名'华秋商城'")

        # 检查是否包含关键词模式
        if keyword and not any(kw in title for kw in ["价格", "库存", "参数", "数据手册"]):
            issues.append("标题缺少关键信息词(价格/库存/参数/数据手册)")

        if issues:
            return AuditResult("Title", "WARN", f"标题: {title[:50]}... 问题: {'; '.join(issues)}", "P0",
                               {"title": title, "length": len(title)},
                               "建议使用模板: {型号} 价格、库存、参数与数据手册 | 华秋商城")

        return AuditResult("Title", "PASS", f"标题: {title[:50]}...", "P0", {"title": title, "length": len(title)})

    def audit_description(self) -> AuditResult:
        """检查Description"""
        if not self.soup:
            return AuditResult("Description", "FAIL", "无法获取页面内容", "P1")

        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        if not meta_desc or not meta_desc.get("content"):
            return AuditResult("Description", "FAIL", "缺少Description标签", "P1")

        desc = meta_desc.get("content").strip()
        issues = []

        # 检查长度
        if len(desc) < 50:
            issues.append("描述过短")
        elif len(desc) > 160:
            issues.append("描述过长，可能在搜索结果中被截断")

        # 检查是否机械重复型号
        keyword = self._extract_keyword()
        if keyword and desc.count(keyword) > 2:
            issues.append(f"型号 '{keyword}' 重复出现 {desc.count(keyword)} 次，文案机械")

        # 检查绝对化表述
        absolute_words = ["最低", "最好", "最优", "全网最", "唯一", "第一"]
        for word in absolute_words:
            if word in desc:
                issues.append(f"使用了绝对化表述: '{word}'")

        # 检查承诺内容是否存在
        promised_content = []
        if "应用电路" in desc:
            promised_content.append("应用电路")
        if "引脚图" in desc:
            promised_content.append("引脚图")
        if "应用案例" in desc:
            promised_content.append("应用案例")
        if "数据手册" in desc:
            promised_content.append("数据手册")

        if promised_content and not self._check_content_availability(promised_content):
            issues.append(f"Description承诺了 {', '.join(promised_content)}，但页面可能未提供对应内容")

        if issues:
            return AuditResult("Description", "WARN", f"问题: {'; '.join(issues)}", "P1",
                               {"description": desc[:100] + "..."})

        return AuditResult("Description", "PASS", f"描述: {desc[:50]}...", "P1")

    def _check_content_availability(self, content_types: List[str]) -> bool:
        """检查页面是否包含特定内容类型"""
        if not self.soup:
            return False

        text = self.soup.get_text().lower()
        for content_type in content_types:
            if content_type.lower() in text:
                return True
        return False

    def audit_keywords(self) -> AuditResult:
        """检查Meta Keywords"""
        if not self.soup:
            return AuditResult("Meta Keywords", "FAIL", "无法获取页面内容", "P2")

        meta_keywords = self.soup.find("meta", attrs={"name": "keywords"})
        if not meta_keywords or not meta_keywords.get("content"):
            return AuditResult("Meta Keywords", "INFO", "Meta Keywords标签已省略（Google不使用）", "P2")

        keywords = meta_keywords.get("content").strip()
        return AuditResult("Meta Keywords", "INFO", f"已存在Keywords: {keywords[:50]}... (Google不使用，维护收益很低)",
                           "P2")

    def audit_robots(self) -> AuditResult:
        """检查Robots Meta标签"""
        if not self.soup:
            return AuditResult("Robots Meta", "FAIL", "无法获取页面内容", "P0")

        meta_robots = self.soup.find("meta", attrs={"name": "robots"})
        if not meta_robots or not meta_robots.get("content"):
            return AuditResult("Robots Meta", "FAIL", "缺少Robots Meta标签", "P0")

        content = meta_robots.get("content").lower()

        # 检查是否有冲突指令
        has_index = "index" in content
        has_noindex = "noindex" in content
        has_follow = "follow" in content
        has_nofollow = "nofollow" in content

        issues = []

        if has_index and has_noindex:
            issues.append("同时包含index和noindex指令，存在冲突")

        if has_follow and has_nofollow:
            issues.append("同时包含follow和nofollow指令，存在冲突")

        if issues:
            return AuditResult("Robots Meta", "FAIL", f"Robots: {content} 问题: {'; '.join(issues)}", "P0")

        # 根据页面类型判断建议
        page_type, type_desc = self.detect_page_type()
        expected_content = ""

        if page_type == "exact_model":
            expected_content = "index,follow"
        else:
            expected_content = "noindex,follow"

        if expected_content and content != expected_content:
            return AuditResult("Robots Meta", "WARN",
                               f"Robots: {content}，建议: {expected_content} (页面类型: {type_desc})", "P0",
                               {"current": content, "suggested": expected_content})

        return AuditResult("Robots Meta", "PASS", f"Robots: {content}", "P0")

    def audit_canonical(self) -> AuditResult:
        """检查Canonical标签"""
        if not self.soup:
            return AuditResult("Canonical", "FAIL", "无法获取页面内容", "P0")

        link_canonical = self.soup.find("link", attrs={"rel": "canonical"})
        if not link_canonical or not link_canonical.get("href"):
            return AuditResult("Canonical", "FAIL", "缺少Canonical标签", "P0")

        canonical_url = link_canonical.get("href")
        parsed_canonical = urlparse(canonical_url)

        issues = []

        # 检查协议
        if parsed_canonical.scheme != "https":
            issues.append(f"Canonical使用非HTTPS协议: {parsed_canonical.scheme}")

        # 检查域名
        if parsed_canonical.netloc != self.parsed_url.netloc:
            issues.append(f"Canonical域名与页面域名不一致: {parsed_canonical.netloc} vs {self.parsed_url.netloc}")

        # 检查是否包含跟踪参数
        canonical_query = parse_qs(parsed_canonical.query)
        tracking_params = ["hq_source", "spm", "utm_"]
        has_tracking = any(p in canonical_query for p in tracking_params)
        if has_tracking:
            issues.append("Canonical URL包含跟踪参数，应从Canonical中删除")

        # 检查是否包含筛选/排序参数（对于精确型号页面）
        page_type, _ = self.detect_page_type()
        if page_type == "exact_model" and parsed_canonical.query:
            issues.append(f"精确型号页面的Canonical包含查询参数: {parsed_canonical.query}")

        if issues:
            return AuditResult("Canonical", "WARN", f"Canonical: {canonical_url} 问题: {'; '.join(issues)}", "P0",
                               {"canonical": canonical_url})

        return AuditResult("Canonical", "PASS", f"Canonical: {canonical_url}", "P0")

    def audit_h_tags(self) -> AuditResult:
        """检查H1-H6标签结构"""
        if not self.soup:
            return AuditResult("H标签结构", "FAIL", "无法获取页面内容", "P0")

        issues = []
        details = {}

        # 检查H1
        h1_tags = self.soup.find_all("h1")
        details["h1_count"] = len(h1_tags)

        if len(h1_tags) == 0:
            issues.append("缺少H1标签")
        elif len(h1_tags) > 1:
            h1_texts = [h.get_text().strip()[:30] for h in h1_tags]
            issues.append(f"存在 {len(h1_tags)} 个H1标签: {h1_texts}")

            # 检查是否有Logo H1
            for h1 in h1_tags:
                text = h1.get_text().strip().lower()
                if "logo" in text or "华秋" in text and "搜索" not in text:
                    issues.append("Logo不应占用页面主标题语义")

        # 检查H2
        h2_tags = self.soup.find_all("h2")
        details["h2_count"] = len(h2_tags)

        # 检查导航是否使用H2
        for h2 in h2_tags:
            # 检查H2是否包裹导航
            parent = h2.parent
            while parent:
                if parent.name == "nav":
                    issues.append("导航不应使用H2标签包裹")
                    break
                parent = parent.parent

        # 检查H1是否是搜索词
        keyword = self._extract_keyword()
        if keyword and h1_tags:
            h1_text = h1_tags[0].get_text().strip()
            if keyword not in h1_text:
                issues.append(f"H1内容 '{h1_text}' 与搜索词 '{keyword}' 不一致")

        if issues:
            return AuditResult("H标签结构", "WARN", f"问题: {'; '.join(issues)}", "P0", details)

        return AuditResult("H标签结构", "PASS", f"H1: {len(h1_tags)}个, H2: {len(h2_tags)}个", "P0", details)

    def audit_initial_html(self) -> AuditResult:
        """检查初始HTML是否包含商品内容"""
        if not self.soup:
            return AuditResult("初始HTML内容", "FAIL", "无法获取页面内容", "P0")

        # 检查是否有商品内容
        has_product = False
        product_fields = ["型号", "品牌", "封装", "价格", "库存"]
        found_fields = []

        # 检查HTML中是否包含商品相关文本
        html_text = str(self.soup)

        # 检查Vue模板 - 如果有Vue模板则可能依赖客户端渲染
        vue_patterns = ["v-for", "v-if", "v-else", "v-bind", "v-model", "v-on", "{{"]
        has_vue_template = any(pattern in html_text for pattern in vue_patterns)

        for field in product_fields:
            if field in html_text:
                found_fields.append(field)

        if len(found_fields) >= 3:
            has_product = True

        details = {
            "has_product": has_product,
            "found_fields": found_fields,
            "has_vue_template": has_vue_template
        }

        if has_product and not has_vue_template:
            return AuditResult("初始HTML内容", "PASS", "初始HTML包含商品内容，未发现Vue模板依赖", "P0", details)
        elif has_product and has_vue_template:
            return AuditResult("初始HTML内容", "WARN", "初始HTML包含商品内容，但存在Vue模板，部分内容可能依赖客户端渲染",
                               "P0", details)
        else:
            return AuditResult("初始HTML内容", "FAIL", "初始HTML未包含商品内容，可能完全依赖客户端渲染", "P0", details)

    def audit_images(self) -> AuditResult:
        """检查图片策略"""
        if not self.soup:
            return AuditResult("图片策略", "FAIL", "无法获取页面内容", "P1")

        images = self.soup.find_all("img")
        if not images:
            return AuditResult("图片策略", "WARN", "页面未找到图片元素", "P1")

        issues = []
        details = {"total": len(images)}
        alt_issues = []
        size_issues = []

        for img in images:
            # 检查alt
            alt = img.get("alt", "")
            src = img.get("src", "")

            # 检查data-src（懒加载）
            data_src = img.get("data-src", "")
            if data_src and not src:
                issues.append(f"图片 {data_src[:30]}... 使用data-src，初始HTML中没有原生img")

            # 检查alt
            if not alt:
                alt_issues.append("缺少alt属性")
            elif len(alt) > 100:
                alt_issues.append(f"alt文本过长 ({len(alt)}字符)")
            elif alt and any(word in alt.lower() for word in ["价格", "库存", "采购"]):
                alt_issues.append("alt中不应堆砌'价格/库存/采购'等关键词")

            # 检查宽高
            if not img.get("width") and not img.get("height") and not img.get("style"):
                size_issues.append("未设置宽高")

        if alt_issues:
            issues.append(f"Alt问题: {'; '.join(set(alt_issues))}")
        if size_issues:
            issues.append(f"尺寸问题: {'; '.join(set(size_issues))}")

        details["alt_issues"] = len(alt_issues)
        details["size_issues"] = len(size_issues)

        if issues:
            return AuditResult("图片策略", "WARN", f"问题: {'; '.join(issues)}", "P1", details)

        return AuditResult("图片策略", "PASS", f"共 {len(images)} 张图片", "P1", details)

    def audit_links(self) -> AuditResult:
        """检查链接策略"""
        if not self.soup:
            return AuditResult("链接策略", "FAIL", "无法获取页面内容", "P0")

        # 检查商品详情链接
        # 查找包含商品链接的a标签
        product_links = []
        for a in self.soup.find_all("a", href=True):
            href = a.get("href")
            if "/item/" in href or "/product/" in href:
                product_links.append(href)

        if not product_links:
            return AuditResult("链接策略", "FAIL", "未找到商品详情链接 (pattern: /item/ 或 /product/)", "P0")

        # 检查分页链接
        page_links = []
        for a in self.soup.find_all("a", href=True):
            href = a.get("href")
            if "page=" in href or "p=" in href:
                page_links.append(href)

        details = {
            "product_links": len(product_links),
            "page_links": len(page_links)
        }

        if product_links:
            return AuditResult("链接策略", "PASS",
                               f"找到 {len(product_links)} 个商品详情链接，{len(page_links)} 个分页链接", "P0", details)
        else:
            return AuditResult("链接策略", "FAIL", "未找到商品详情链接", "P0", details)

    def audit_pc_m_relation(self) -> AuditResult:
        """检查PC/M关系"""
        if not self.soup:
            return AuditResult("PC/M关系", "FAIL", "无法获取页面内容", "P0")

        # 检查alternate link (PC/M)
        alternate_links = self.soup.find_all("link", attrs={"rel": "alternate"})
        mobile_links = []

        for link in alternate_links:
            media = link.get("media", "")
            href = link.get("href", "")
            if "640px" in media or "mobile" in media:
                mobile_links.append(href)

        # 检查mobile-agent
        mobile_agent = self.soup.find("meta", attrs={"name": "mobile-agent"})

        details = {
            "alternate_links": len(alternate_links),
            "mobile_links": len(mobile_links),
            "has_mobile_agent": bool(mobile_agent)
        }

        if not mobile_links and not mobile_agent:
            return AuditResult("PC/M关系", "FAIL", "未找到PC/M关联 (alternate或mobile-agent)", "P0", details)

        if not mobile_links:
            return AuditResult("PC/M关系", "WARN", "找到mobile-agent但缺少alternate link", "P0", details)

        if mobile_agent:
            return AuditResult("PC/M关系", "PASS", "找到PC/M关联 (alternate + mobile-agent)", "P0", details)
        else:
            return AuditResult("PC/M关系", "WARN", "找到alternate但缺少mobile-agent", "P0", details)

    def audit_viewport(self) -> AuditResult:
        """检查viewport"""
        if not self.soup:
            return AuditResult("Viewport", "FAIL", "无法获取页面内容", "P0")

        meta_viewport = self.soup.find("meta", attrs={"name": "viewport"})
        if not meta_viewport or not meta_viewport.get("content"):
            return AuditResult("Viewport", "FAIL", "缺少Viewport标签", "P0")

        content = meta_viewport.get("content").lower()

        # 检查是否禁止缩放
        if "user-scalable=no" in content or "maximum-scale=1.0" in content and "user-scalable=no" not in content:
            return AuditResult("Viewport", "FAIL", "Viewport禁止缩放，存在可访问性问题", "P0", {"viewport": content})

        if "width=device-width" in content:
            return AuditResult("Viewport", "PASS", "Viewport配置正确", "P0", {"viewport": content})

        return AuditResult("Viewport", "WARN", f"Viewport: {content}，建议: width=device-width, initial-scale=1.0", "P0",
                           {"viewport": content})

    def audit_structured_data(self) -> AuditResult:
        """检查结构化数据"""
        if not self.soup:
            return AuditResult("结构化数据", "FAIL", "无法获取页面内容", "P1")

        # 查找JSON-LD
        script_tags = self.soup.find_all("script", attrs={"type": "application/ld+json"})

        if not script_tags:
            return AuditResult("结构化数据", "FAIL", "未找到JSON-LD结构化数据", "P1")

        # 检查是否有BreadcrumbList
        has_breadcrumb = False
        breadcrumb_data = None

        for script in script_tags:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") == "BreadcrumbList":
                        has_breadcrumb = True
                        breadcrumb_data = data
                    elif isinstance(data.get("@type"), list) and "BreadcrumbList" in data.get("@type"):
                        has_breadcrumb = True
                        breadcrumb_data = data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "BreadcrumbList":
                            has_breadcrumb = True
                            breadcrumb_data = item
                            break
            except:
                continue

        if has_breadcrumb:
            return AuditResult("结构化数据", "PASS", "找到BreadcrumbList结构化数据", "P1", {"has_breadcrumb": True})
        else:
            return AuditResult("结构化数据", "FAIL", "找到JSON-LD但缺少BreadcrumbList", "P1", {"has_breadcrumb": False})

    def audit_status_code(self) -> AuditResult:
        """检查HTTP状态码"""
        if not self.response:
            return AuditResult("HTTP状态码", "FAIL", "无法获取响应", "P0")

        status = self.response.status_code

        # 检查页面类型并验证状态码
        page_type, type_desc = self.detect_page_type()

        if status == 200:
            return AuditResult("HTTP状态码", "PASS", f"状态码: {status}", "P0",
                               {"status": status, "page_type": page_type})
        elif status == 404:
            return AuditResult("HTTP状态码", "FAIL", f"状态码: {status} (页面未找到)", "P0", {"status": status})
        elif status >= 400:
            return AuditResult("HTTP状态码", "FAIL", f"状态码: {status} (错误页面)", "P0", {"status": status})
        else:
            return AuditResult("HTTP状态码", "WARN", f"状态码: {status}", "P0", {"status": status})

    def audit_page_type(self) -> AuditResult:
        """检查页面类型和收录策略"""
        page_type, type_desc = self.detect_page_type()

        # 检查是否符合收录策略
        expected_robots = "index,follow" if page_type == "exact_model" else "noindex,follow"

        # 获取实际的robots
        meta_robots = self.soup.find("meta", attrs={"name": "robots"})
        actual_robots = meta_robots.get("content") if meta_robots else "未设置"

        details = {
            "page_type": page_type,
            "type_desc": type_desc,
            "expected_robots": expected_robots,
            "actual_robots": actual_robots
        }

        if page_type == "exact_model":
            return AuditResult("页面类型与收录", "PASS", f"精确型号主页面，应允许索引", "P0", details)
        else:
            return AuditResult("页面类型与收录", "INFO", f"{type_desc}，默认不应索引", "P0", details)

    def run_full_audit(self) -> PageAudit:
        """执行完整审计"""
        audit = PageAudit(url=self.url)

        if not self.fetch():
            audit.add_result(AuditResult("页面获取", "FAIL", f"无法获取页面: {self.url}", "P0"))
            return audit

        # P0 检查项
        audit.add_result(self.audit_status_code())
        audit.add_result(self.audit_html_lang())
        audit.add_result(self.audit_title())
        audit.add_result(self.audit_robots())
        audit.add_result(self.audit_canonical())
        audit.add_result(self.audit_h_tags())
        audit.add_result(self.audit_initial_html())
        audit.add_result(self.audit_links())
        audit.add_result(self.audit_pc_m_relation())
        audit.add_result(self.audit_viewport())
        audit.add_result(self.audit_page_type())

        # P1 检查项
        audit.add_result(self.audit_description())
        audit.add_result(self.audit_images())
        audit.add_result(self.audit_structured_data())

        # P2 检查项
        audit.add_result(self.audit_keywords())

        return audit


def generate_html_report(audit: PageAudit) -> str:
    """生成HTML格式的审计报告"""
    summary = audit.get_summary()

    # 按优先级分组结果
    p0_results = [r for r in audit.results if r.priority == "P0"]
    p1_results = [r for r in audit.results if r.priority == "P1"]
    p2_results = [r for r in audit.results if r.priority == "P2"]

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEO审计报告 - {audit.url}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; 
                      box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .url {{ color: #666; word-break: break-all; }}
            .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                        gap: 15px; margin: 20px 0; }}
            .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat .number {{ font-size: 2em; font-weight: bold; }}
            .stat .label {{ color: #666; font-size: 0.9em; }}
            .stat.pass .number {{ color: #28a745; }}
            .stat.fail .number {{ color: #dc3545; }}
            .stat.warn .number {{ color: #ffc107; }}
            .stat.info .number {{ color: #17a2b8; }}
            .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; 
                       box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .section h2 {{ margin-top: 0; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }}
            .check {{ padding: 12px; margin: 8px 0; border-left: 4px solid #6c757d; 
                     background: #f8f9fa; border-radius: 4px; }}
            .check.PASS {{ border-left-color: #28a745; background: #f0fff4; }}
            .check.FAIL {{ border-left-color: #dc3545; background: #fff5f5; }}
            .check.WARN {{ border-left-color: #ffc107; background: #fffcf0; }}
            .check.INFO {{ border-left-color: #17a2b8; background: #f0f8ff; }}
            .check .name {{ font-weight: bold; }}
            .check .priority {{ display: inline-block; padding: 2px 8px; border-radius: 4px; 
                               font-size: 0.8em; font-weight: bold; margin-left: 10px; }}
            .priority-P0 {{ background: #dc3545; color: white; }}
            .priority-P1 {{ background: #ffc107; color: #333; }}
            .priority-P2 {{ background: #6c757d; color: white; }}
            .check .message {{ margin-top: 5px; color: #495057; }}
            .check .details {{ margin-top: 5px; padding: 8px; background: #f8f9fa; border-radius: 4px; 
                              font-family: monospace; font-size: 0.9em; white-space: pre-wrap; }}
            .check .suggestion {{ margin-top: 5px; color: #28a745; font-style: italic; }}
            .score {{ background: #e9ecef; padding: 10px 20px; border-radius: 20px; 
                     display: inline-block; }}
            .timestamp {{ color: #666; font-size: 0.9em; }}
            @media (max-width: 768px) {{ .summary {{ grid-template-columns: 1fr 1fr; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 SEO 审计报告</h1>
            <p class="url"><strong>URL:</strong> {audit.url}</p>
            <p><strong>审计时间:</strong> {audit.timestamp}</p>
            <p><strong>状态码:</strong> {audit.status_code or 'N/A'}</p>
            <p><strong>内容类型:</strong> {audit.content_type or 'N/A'}</p>
            <div class="score">得分: {summary['score']} ({summary['pass_rate']})</div>
        </div>

        <div class="summary">
            <div class="stat pass"><div class="number">{summary['stats'].get('PASS', 0)}</div><div class="label">✅ 通过</div></div>
            <div class="stat fail"><div class="number">{summary['stats'].get('FAIL', 0)}</div><div class="label">❌ 失败</div></div>
            <div class="stat warn"><div class="number">{summary['stats'].get('WARN', 0)}</div><div class="label">⚠️ 警告</div></div>
            <div class="stat info"><div class="number">{summary['stats'].get('INFO', 0)}</div><div class="label">ℹ️ 信息</div></div>
        </div>

        <div class="section">
            <h2>📋 P0 优先级检查项</h2>
            {''.join([_format_check(r) for r in p0_results])}
        </div>

        <div class="section">
            <h2>📋 P1 优先级检查项</h2>
            {''.join([_format_check(r) for r in p1_results])}
        </div>

        <div class="section">
            <h2>📋 P2 优先级检查项</h2>
            {''.join([_format_check(r) for r in p2_results])}
        </div>

        <div class="section">
            <h2>📊 优先级统计</h2>
            <ul>
                <li>P0: 通过 {summary['priority_counts']['P0'].get('PASS', 0)} / 失败 {summary['priority_counts']['P0'].get('FAIL', 0)} / 警告 {summary['priority_counts']['P0'].get('WARN', 0)}</li>
                <li>P1: 通过 {summary['priority_counts']['P1'].get('PASS', 0)} / 失败 {summary['priority_counts']['P1'].get('FAIL', 0)} / 警告 {summary['priority_counts']['P1'].get('WARN', 0)}</li>
                <li>P2: 通过 {summary['priority_counts']['P2'].get('PASS', 0)} / 失败 {summary['priority_counts']['P2'].get('FAIL', 0)} / 警告 {summary['priority_counts']['P2'].get('WARN', 0)}</li>
            </ul>
        </div>

        <div class="section" style="background: #f8f9fa;">
            <p class="timestamp">报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="font-size: 0.9em; color: #666;">基于华秋商城 SEO 现状审计与改版策略文档 V0.8</p>
        </div>
    </body>
    </html>
    """
    return html


def _format_check(result: AuditResult) -> str:
    """格式化单个检查结果为HTML"""
    status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
    details_html = ""
    if result.details:
        details_html = f'<div class="details">{json.dumps(result.details, ensure_ascii=False, indent=2)}</div>'
    suggestion_html = f'<div class="suggestion">💡 {result.suggestion}</div>' if result.suggestion else ""

    return f"""
    <div class="check {result.status}">
        <span class="name">{status_emoji.get(result.status, '')} {result.check_name}</span>
        <span class="priority priority-{result.priority}">{result.priority}</span>
        <div class="message">{result.message}</div>
        {details_html}
        {suggestion_html}
    </div>
    """


def print_console_report(audit: PageAudit):
    """在控制台打印审计报告"""
    console = Console()

    console.print(Panel(f"[bold]🔍 SEO 审计报告[/bold]\nURL: {audit.url}\n时间: {audit.timestamp}",
                        title="华秋商城 SEO", border_style="blue"))

    summary = audit.get_summary()

    table = Table(title="审计摘要", show_header=True, header_style="bold cyan")
    table.add_column("状态", style="bold")
    table.add_column("数量", justify="right")

    for status, count in summary["stats"].items():
        emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
        table.add_row(f"{emoji.get(status, '')} {status}", str(count))

    table.add_row("", "")
    table.add_row("📊 总分", f"{summary['score']} ({summary['pass_rate']})")
    console.print(table)

    # 按优先级显示结果
    for priority in ["P0", "P1", "P2"]:
        priority_results = [r for r in audit.results if r.priority == priority]
        if priority_results:
            pri_table = Table(title=f"{priority} 检查项", show_header=True, header_style="bold")
            pri_table.add_column("检查项", style="cyan")
            pri_table.add_column("状态", style="bold")
            pri_table.add_column("详情")

            for r in priority_results:
                status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
                status_icon = status_emoji.get(r.status, "")
                pri_table.add_row(r.check_name, f"{status_icon} {r.status}",
                                  r.message[:100] + ("..." if len(r.message) > 100 else ""))

            console.print(pri_table)


def main():
    parser = argparse.ArgumentParser(description="华秋商城 SEO 标准化检测脚本")
    parser.add_argument("--url", "-u", required=True, help="要审计的URL")
    parser.add_argument("--output", "-o", help="输出HTML报告文件路径")
    parser.add_argument("--json", "-j", action="store_true", help="输出JSON格式")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="请求超时时间(秒)")

    args = parser.parse_args()

    auditor = SEOAuditor(args.url, timeout=args.timeout)
    audit = auditor.run_full_audit()

    if args.json:
        print(json.dumps({
            "url": audit.url,
            "timestamp": audit.timestamp,
            "status_code": audit.status_code,
            "summary": audit.get_summary(),
            "results": [{"check": r.check_name, "status": r.status, "message": r.message,
                         "priority": r.priority, "details": r.details} for r in audit.results]
        }, ensure_ascii=False, indent=2))
    elif args.output:
        html = generate_html_report(audit)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 HTML报告已生成: {args.output}")

        # 同时输出简要统计到控制台
        summary = audit.get_summary()
        print(f"\n📊 审计结果: {summary['score']} ({summary['pass_rate']})")
        print(f"   ✅ 通过: {summary['stats'].get('PASS', 0)}")
        print(f"   ❌ 失败: {summary['stats'].get('FAIL', 0)}")
        print(f"   ⚠️ 警告: {summary['stats'].get('WARN', 0)}")
        print(f"   ℹ️ 信息: {summary['stats'].get('INFO', 0)}")
    else:
        print_console_report(audit)


if __name__ == "__main__":
    main()