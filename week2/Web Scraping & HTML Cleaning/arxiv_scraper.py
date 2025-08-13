#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv Paper Abstract Scraper
查询指定子类别的最新200篇论文，抓取摘要页面并清理内容
使用Trafilatura清理HTML，使用Tesseract OCR从截图中提取文本
"""

import json
import requests
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import sys

# 导入依赖库
try:
    import trafilatura
    from PIL import Image
    import pytesseract
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages:")
    print("pip install trafilatura pytesseract selenium pillow")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArxivScraper:
    def __init__(self, category: str = "cs.CL", max_results: int = 200):
        """
        初始化arXiv抓取器
        
        Args:
            category: arXiv子类别 (例如: cs.CL, cs.AI, cs.LG)
            max_results: 最大抓取结果数量
        """
        self.category = category
        self.max_results = max_results
        self.base_url = "http://export.arxiv.org/api/query"
        self.abs_base_url = "https://arxiv.org/abs/"
        self.results = []
        
        # 设置Chrome选项用于截图
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # 无头模式
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
    def query_arxiv_api(self) -> List[Dict]:
        """
        通过arXiv API查询论文
        
        Returns:
            包含论文信息的字典列表
        """
        logger.info(f"开始查询arXiv API，类别: {self.category}, 最大结果数: {self.max_results}")
        
        # 构建查询参数
        params = {
            'search_query': f'cat:{self.category}',
            'start': 0,
            'max_results': self.max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析XML响应
            root = ET.fromstring(response.content)
            entries = []
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                # 提取基本信息
                paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text
                arxiv_id = paper_id.split('/')[-1]
                
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                
                # 提取作者
                authors = []
                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                    name = author.find('{http://www.w3.org/2005/Atom}name').text
                    authors.append(name)
                
                # 提取日期
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                date = published.split('T')[0]  # 只取日期部分
                
                entries.append({
                    'arxiv_id': arxiv_id,
                    'url': f"https://arxiv.org/abs/{arxiv_id}",
                    'title': title,
                    'abstract': summary,
                    'authors': authors,
                    'date': date
                })
                
            logger.info(f"成功获取 {len(entries)} 篇论文信息")
            return entries
            
        except Exception as e:
            logger.error(f"查询arXiv API失败: {e}")
            return []
    
    def scrape_abstract_page(self, paper: Dict) -> Dict:
        """
        抓取单个论文的摘要页面并使用Trafilatura清理
        
        Args:
            paper: 包含论文信息的字典
            
        Returns:
            更新后的论文信息字典
        """
        try:
            # 获取摘要页面HTML
            response = requests.get(paper['url'], timeout=30)
            response.raise_for_status()
            
            # 使用Trafilatura提取清理后的内容
            extracted = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=False,
                include_formatting=True
            )
            
            if extracted:
                # 使用Trafilatura提取的内容更新摘要
                paper['trafilatura_content'] = extracted
                logger.debug(f"成功使用Trafilatura处理: {paper['arxiv_id']}")
            else:
                paper['trafilatura_content'] = paper['abstract']  # 回退到原始摘要
                
        except Exception as e:
            logger.error(f"抓取页面失败 {paper['url']}: {e}")
            paper['trafilatura_content'] = paper['abstract']  # 回退到原始摘要
            
        return paper
    
    def take_screenshot_and_ocr(self, paper: Dict) -> Dict:
        """
        对摘要页面截图并使用Tesseract OCR提取文本
        
        Args:
            paper: 包含论文信息的字典
            
        Returns:
            包含OCR结果的更新字典
        """
        driver = None
        try:
            # 创建WebDriver实例
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # 访问摘要页面
            driver.get(paper['url'])
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "abstract"))
            )
            
            # 截图保存到临时文件
            screenshot_path = f"temp_screenshot_{paper['arxiv_id']}.png"
            driver.save_screenshot(screenshot_path)
            
            # 使用Tesseract OCR提取文本
            image = Image.open(screenshot_path)
            ocr_text = pytesseract.image_to_string(image, config='--psm 6')
            
            paper['ocr_text'] = ocr_text.strip()
            
            # 删除临时截图文件
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                
            logger.debug(f"成功完成OCR处理: {paper['arxiv_id']}")
            
        except Exception as e:
            logger.error(f"截图或OCR处理失败 {paper['url']}: {e}")
            paper['ocr_text'] = ""
        finally:
            if driver:
                driver.quit()
                
        return paper
    
    def process_papers(self) -> List[Dict]:
        """
        处理所有论文：抓取页面、清理内容、OCR提取
        
        Returns:
            处理后的论文列表
        """
        papers = self.query_arxiv_api()
        if not papers:
            return []
        
        processed_papers = []
        
        for i, paper in enumerate(papers):
            logger.info(f"处理论文 {i+1}/{len(papers)}: {paper['arxiv_id']}")
            
            # 抓取并清理摘要页面
            paper = self.scrape_abstract_page(paper)
            
            # 截图并OCR (每10篇论文进行OCR，避免过度使用资源)
            if i % 10 == 0:  # 只对部分论文进行OCR处理
                paper = self.take_screenshot_and_ocr(paper)
            else:
                paper['ocr_text'] = ""  # 其他论文设为空字符串
            
            # 创建最终的数据结构
            final_paper = {
                'url': paper['url'],
                'title': paper['title'],
                'abstract': paper['abstract'],  # 原始摘要
                'authors': paper['authors'],
                'date': paper['date']
            }
            
            # 如果Trafilatura提取了更好的内容，使用它
            if 'trafilatura_content' in paper and len(paper['trafilatura_content']) > len(paper['abstract']):
                final_paper['abstract'] = paper['trafilatura_content']
            
            # 如果OCR提取了有用的文本，添加到摘要中
            if paper.get('ocr_text') and len(paper['ocr_text'].strip()) > 50:
                final_paper['abstract'] += f"\n\n[OCR提取内容]: {paper['ocr_text'][:500]}..."
            
            processed_papers.append(final_paper)
            
            # 添加延迟以避免过度请求
            time.sleep(1)
        
        return processed_papers
    
    def save_to_json(self, papers: List[Dict], filename: str = "arxiv_clean.json") -> bool:
        """
        将处理后的论文数据保存为JSON文件
        
        Args:
            papers: 论文数据列表
            filename: 输出文件名
            
        Returns:
            保存是否成功
        """
        try:
            # 检查文件大小限制 (1MB)
            temp_data = json.dumps(papers, ensure_ascii=False, indent=2)
            if len(temp_data.encode('utf-8')) > 1024 * 1024:  # 1MB
                logger.warning("数据大小超过1MB限制，将截断数据")
                # 如果数据过大，减少论文数量
                while len(temp_data.encode('utf-8')) > 1024 * 1024 and papers:
                    papers = papers[:-10]  # 每次移除10篇论文
                    temp_data = json.dumps(papers, ensure_ascii=False, indent=2)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(papers, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(filename)
            logger.info(f"成功保存 {len(papers)} 篇论文到 {filename}")
            logger.info(f"文件大小: {file_size / 1024:.2f} KB")
            
            return True
            
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return False

def main():
    """主函数"""
    # 创建抓取器实例
    scraper = ArxivScraper(category="cs.CL", max_results=200)
    
    # 处理论文
    papers = scraper.process_papers()
    
    if papers:
        # 保存结果
        success = scraper.save_to_json(papers)
        if success:
            print(f"成功完成！共处理 {len(papers)} 篇论文，保存到 arxiv_clean.json")
        else:
            print("保存文件失败")
    else:
        print("未能获取任何论文数据")

if __name__ == "__main__":
    main()
