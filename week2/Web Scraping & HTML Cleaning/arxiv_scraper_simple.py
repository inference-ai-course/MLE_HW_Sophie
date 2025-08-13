#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版arXiv论文摘要抓取器
主要使用API和Trafilatura进行数据提取和清理
"""

import json
import requests
import time
import logging
from typing import List, Dict
import xml.etree.ElementTree as ET
import os
import sys

# 导入依赖库
try:
    import trafilatura
except ImportError:
    print("Missing trafilatura package. Please install it:")
    print("pip install trafilatura")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleArxivScraper:
    def __init__(self, category: str = "cs.CL", max_results: int = 200):
        """
        初始化简化版arXiv抓取器
        
        Args:
            category: arXiv子类别 (例如: cs.CL, cs.AI, cs.LG)
            max_results: 最大抓取结果数量
        """
        self.category = category
        self.max_results = max_results
        self.base_url = "http://export.arxiv.org/api/query"
        
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
            
            # 获取命名空间
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                # 提取基本信息
                paper_id = entry.find('atom:id', ns).text
                arxiv_id = paper_id.split('/')[-1]
                
                title = entry.find('atom:title', ns).text.strip()
                title = ' '.join(title.split())  # 清理多余空格和换行
                
                summary = entry.find('atom:summary', ns).text.strip()
                summary = ' '.join(summary.split())  # 清理多余空格和换行
                
                # 提取作者
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns).text
                    authors.append(name)
                
                # 提取日期
                published = entry.find('atom:published', ns).text
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
    
    def enhance_with_trafilatura(self, papers: List[Dict]) -> List[Dict]:
        """
        使用Trafilatura增强论文信息
        
        Args:
            papers: 论文信息列表
            
        Returns:
            增强后的论文信息列表
        """
        enhanced_papers = []
        
        for i, paper in enumerate(papers):
            logger.info(f"处理论文 {i+1}/{len(papers)}: {paper['arxiv_id']}")
            
            try:
                # 获取摘要页面HTML
                response = requests.get(paper['url'], timeout=15)
                response.raise_for_status()
                
                # 使用Trafilatura提取清理后的内容
                extracted = trafilatura.extract(
                    response.text,
                    include_comments=False,
                    include_tables=True,
                    include_formatting=True,
                    include_links=False
                )
                
                if extracted and len(extracted.strip()) > len(paper['abstract']):
                    # 如果Trafilatura提取的内容更丰富，使用它
                    paper['abstract'] = extracted.strip()
                    logger.debug(f"使用Trafilatura增强内容: {paper['arxiv_id']}")
                
                # 添加延迟以避免过度请求
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Trafilatura处理失败 {paper['url']}: {e}")
                # 继续使用原始摘要
            
            enhanced_papers.append({
                'url': paper['url'],
                'title': paper['title'],
                'abstract': paper['abstract'],
                'authors': paper['authors'],
                'date': paper['date']
            })
        
        return enhanced_papers
    
    def save_to_json(self, papers: List[Dict], filename: str = "arxiv_clean.json") -> bool:
        """
        保存论文数据到JSON文件，确保文件大小不超过1MB
        
        Args:
            papers: 论文数据列表
            filename: 输出文件名
            
        Returns:
            保存是否成功
        """
        try:
            # 检查文件大小限制 (1MB)
            temp_data = json.dumps(papers, ensure_ascii=False, indent=2)
            original_count = len(papers)
            
            # 如果数据超过1MB，逐步减少论文数量
            while len(temp_data.encode('utf-8')) > 1024 * 1024 and papers:
                papers = papers[:-5]  # 每次移除5篇论文
                temp_data = json.dumps(papers, ensure_ascii=False, indent=2)
            
            if len(papers) < original_count:
                logger.warning(f"为满足1MB限制，论文数量从 {original_count} 减少到 {len(papers)}")
            
            # 保存到文件
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
    print("=== arXiv论文摘要抓取器 ===")
    print("正在抓取cs.CL类别的最新200篇论文...")
    
    # 创建抓取器实例
    scraper = SimpleArxivScraper(category="cs.CL", max_results=200)
    
    # 查询论文
    papers = scraper.query_arxiv_api()
    
    if not papers:
        print("未能获取任何论文数据")
        return
    
    print(f"成功获取 {len(papers)} 篇论文信息")
    print("正在使用Trafilatura增强内容...")
    
    # 使用Trafilatura增强内容
    enhanced_papers = scraper.enhance_with_trafilatura(papers)
    
    # 保存结果
    success = scraper.save_to_json(enhanced_papers)
    
    if success:
        print(f"✅ 任务完成！共处理 {len(enhanced_papers)} 篇论文")
        print("📁 数据已保存到 arxiv_clean.json")
        
        # 显示一些统计信息
        avg_abstract_length = sum(len(p['abstract']) for p in enhanced_papers) / len(enhanced_papers)
        print(f"📊 平均摘要长度: {avg_abstract_length:.0f} 字符")
        
        # 显示第一篇论文作为示例
        if enhanced_papers:
            first_paper = enhanced_papers[0]
            print(f"\n📄 示例论文:")
            print(f"标题: {first_paper['title'][:100]}...")
            print(f"作者: {', '.join(first_paper['authors'][:3])}{'...' if len(first_paper['authors']) > 3 else ''}")
            print(f"日期: {first_paper['date']}")
            print(f"摘要: {first_paper['abstract'][:200]}...")
    else:
        print("❌ 保存文件失败")

if __name__ == "__main__":
    main()
