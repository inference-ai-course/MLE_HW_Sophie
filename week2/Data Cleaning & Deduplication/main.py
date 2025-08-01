#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Cleaning & Deduplication Pipeline
端到端数据清理和去重管道

功能：
1. 语言检测
2. HTML噪声去除
3. MinHash去重 (相似度≥0.7)
4. PII信息去除
5. 重复n-grams去除
"""

import os
import re
import json
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter, defaultdict
import hashlib

# 第三方库
import pandas as pd
import numpy as np
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from bs4 import BeautifulSoup
from datasketch import MinHash, MinHashLSH
import nltk

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清理和去重主类"""
    
    def __init__(self, similarity_threshold: float = 0.7, target_languages: List[str] = ['en', 'zh-cn']):
        """
        初始化数据清理器
        
        Args:
            similarity_threshold: MinHash相似度阈值，默认0.7
            target_languages: 目标语言列表，默认英语和中文
        """
        self.similarity_threshold = similarity_threshold
        self.target_languages = target_languages
        self.stats = {
            'initial_docs': 0,
            'initial_tokens': 0,
            'after_language_detection': 0,
            'after_html_cleaning': 0,
            'after_deduplication': 0,
            'after_pii_removal': 0,
            'after_ngram_removal': 0,
            'final_tokens': 0
        }
        
        # 创建输出目录
        os.makedirs('output', exist_ok=True)
        os.makedirs('sample_data', exist_ok=True)
        
        # PII正则表达式模式
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            'phone': re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        }
    
    def load_sample_data(self) -> List[str]:
        """
        加载示例数据用于测试
        
        Returns:
            文档列表
        """
        sample_docs = [
            "<html><body><h1>Welcome to our website!</h1><p>Contact us at info@example.com or call 555-123-4567</p></body></html>",
            "This is a clean English document without any HTML tags.",
            "<div>Another HTML document with <script>alert('test')</script> and phone number (555) 987-6543</div>",
            "这是一个中文文档，包含一些测试内容。",
            "This is a duplicate document. This is a duplicate document. This is a duplicate document.",
            "<p>Credit card number: 4532-1234-5678-9012 should be removed</p>",
            "Another English document with similar content to test deduplication.",
            "Répétition de texte français. Répétition de texte français. Répétition de texte français.",
            "Clean document number one with unique content.",
            "Clean document number two with different unique content."
        ]
        
        # 添加一些重复的文档来测试去重
        sample_docs.extend([
            "This is a clean English document without any HTML tags.",  # 重复
            "Another English document with similar content to test deduplication.",  # 重复
        ])
        
        logger.info(f"加载了 {len(sample_docs)} 个示例文档")
        return sample_docs
    
    def detect_language(self, documents: List[str]) -> List[str]:
        """
        检测文档语言并过滤
        
        Args:
            documents: 输入文档列表
            
        Returns:
            过滤后的文档列表
        """
        logger.info("开始语言检测...")
        filtered_docs = []
        
        for doc in documents:
            try:
                # 去除HTML标签后检测语言
                clean_text = BeautifulSoup(doc, 'html.parser').get_text()
                if len(clean_text.strip()) < 10:  # 太短的文本跳过
                    continue
                    
                lang = detect(clean_text)
                if lang in self.target_languages:
                    filtered_docs.append(doc)
                else:
                    logger.debug(f"跳过语言 {lang} 的文档")
            except LangDetectException:
                logger.warning("语言检测失败，跳过该文档")
                continue
        
        self.stats['after_language_detection'] = len(filtered_docs)
        logger.info(f"语言检测完成，保留 {len(filtered_docs)} 个文档")
        return filtered_docs
    
    def clean_html(self, documents: List[str]) -> List[str]:
        """
        去除HTML噪声
        
        Args:
            documents: 输入文档列表
            
        Returns:
            清理后的文档列表
        """
        logger.info("开始HTML清理...")
        cleaned_docs = []
        
        for doc in documents:
            # 使用BeautifulSoup去除HTML标签
            soup = BeautifulSoup(doc, 'html.parser')
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取纯文本
            text = soup.get_text()
            
            # 清理多余的空白字符
            text = re.sub(r'\s+', ' ', text).strip()
            
            if text:  # 只保留非空文档
                cleaned_docs.append(text)
        
        self.stats['after_html_cleaning'] = len(cleaned_docs)
        logger.info(f"HTML清理完成，剩余 {len(cleaned_docs)} 个文档")
        return cleaned_docs
    
    def create_minhash(self, text: str, num_perm: int = 128) -> MinHash:
        """
        为文本创建MinHash签名
        
        Args:
            text: 输入文本
            num_perm: 排列数量
            
        Returns:
            MinHash对象
        """
        # 将文本分词（简单的基于空格的分词）
        tokens = text.lower().split()
        
        # 创建MinHash
        minhash = MinHash(num_perm=num_perm)
        for token in tokens:
            minhash.update(token.encode('utf8'))
        
        return minhash
    
    def deduplicate_minhash(self, documents: List[str]) -> List[str]:
        """
        使用MinHash进行去重
        
        Args:
            documents: 输入文档列表
            
        Returns:
            去重后的文档列表
        """
        logger.info("开始MinHash去重...")
        
        # 创建LSH索引
        lsh = MinHashLSH(threshold=self.similarity_threshold, num_perm=128)
        
        # 存储文档和其MinHash
        doc_hashes = {}
        unique_docs = []
        
        for i, doc in enumerate(documents):
            minhash = self.create_minhash(doc)
            doc_id = f"doc_{i}"
            
            # 检查是否有相似文档
            similar_docs = lsh.query(minhash)
            
            if not similar_docs:  # 没有相似文档，添加到索引
                lsh.insert(doc_id, minhash)
                doc_hashes[doc_id] = minhash
                unique_docs.append(doc)
            else:
                logger.debug(f"发现重复文档，跳过文档 {i}")
        
        self.stats['after_deduplication'] = len(unique_docs)
        logger.info(f"MinHash去重完成，剩余 {len(unique_docs)} 个唯一文档")
        return unique_docs
    
    def remove_pii(self, documents: List[str]) -> List[str]:
        """
        去除个人身份信息(PII)
        
        Args:
            documents: 输入文档列表
            
        Returns:
            去除PII后的文档列表
        """
        logger.info("开始PII去除...")
        cleaned_docs = []
        pii_counts = defaultdict(int)
        
        for doc in documents:
            cleaned_doc = doc
            
            # 去除各种PII
            for pii_type, pattern in self.pii_patterns.items():
                matches = pattern.findall(cleaned_doc)
                if matches:
                    pii_counts[pii_type] += len(matches)
                    cleaned_doc = pattern.sub(f'[{pii_type.upper()}_REMOVED]', cleaned_doc)
            
            cleaned_docs.append(cleaned_doc)
        
        # 记录PII去除统计
        for pii_type, count in pii_counts.items():
            logger.info(f"去除了 {count} 个 {pii_type}")
        
        self.stats['after_pii_removal'] = len(cleaned_docs)
        logger.info("PII去除完成")
        return cleaned_docs
    
    def remove_repetitive_ngrams(self, documents: List[str], max_ngram: int = 3, threshold: int = 3) -> List[str]:
        """
        去除重复的n-grams
        
        Args:
            documents: 输入文档列表
            max_ngram: 最大n-gram长度
            threshold: 重复阈值
            
        Returns:
            去除重复n-grams后的文档列表
        """
        logger.info("开始去除重复n-grams...")
        cleaned_docs = []
        
        for doc in documents:
            words = doc.split()
            if len(words) < max_ngram:
                cleaned_docs.append(doc)
                continue
            
            # 检测重复的n-grams
            for n in range(2, max_ngram + 1):
                ngram_counts = Counter()
                ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
                
                for ngram in ngrams:
                    ngram_counts[ngram] += 1
                
                # 去除重复超过阈值的n-grams
                for ngram, count in ngram_counts.items():
                    if count >= threshold:
                        ngram_str = ' '.join(ngram)
                        # 只保留第一次出现，去除后续重复
                        parts = doc.split(ngram_str)
                        if len(parts) > 1:
                            doc = parts[0] + ngram_str + ''.join(parts[1:])
                            logger.debug(f"去除重复n-gram: {ngram_str}")
            
            cleaned_docs.append(doc)
        
        self.stats['after_ngram_removal'] = len(cleaned_docs)
        logger.info("重复n-grams去除完成")
        return cleaned_docs
    
    def count_tokens(self, documents: List[str]) -> int:
        """
        统计文档中的token数量
        
        Args:
            documents: 文档列表
            
        Returns:
            总token数
        """
        total_tokens = 0
        for doc in documents:
            total_tokens += len(doc.split())
        return total_tokens
    
    def process_pipeline(self, input_documents: Optional[List[str]] = None) -> List[str]:
        """
        执行完整的数据清理管道
        
        Args:
            input_documents: 输入文档列表，如果为None则使用示例数据
            
        Returns:
            清理后的文档列表
        """
        logger.info("开始数据清理管道...")
        
        # 加载数据
        if input_documents is None:
            documents = self.load_sample_data()
        else:
            documents = input_documents
        
        # 记录初始统计
        self.stats['initial_docs'] = len(documents)
        self.stats['initial_tokens'] = self.count_tokens(documents)
        
        # 步骤1: 语言检测
        documents = self.detect_language(documents)
        
        # 步骤2: HTML清理
        documents = self.clean_html(documents)
        
        # 步骤3: MinHash去重
        documents = self.deduplicate_minhash(documents)
        
        # 步骤4: PII去除
        documents = self.remove_pii(documents)
        
        # 步骤5: 重复n-grams去除
        documents = self.remove_repetitive_ngrams(documents)
        
        # 记录最终统计
        self.stats['final_tokens'] = self.count_tokens(documents)
        
        logger.info("数据清理管道完成")
        return documents
    
    def save_results(self, clean_documents: List[str]):
        """
        保存清理结果和统计信息
        
        Args:
            clean_documents: 清理后的文档列表
        """
        # 保存清理后的语料库
        with open('output/clean_corpus.txt', 'w', encoding='utf-8') as f:
            for doc in clean_documents:
                f.write(doc + '\n\n')
        
        logger.info(f"保存了 {len(clean_documents)} 个清理后的文档到 output/clean_corpus.txt")
        
        # 生成统计报告
        self.generate_stats_report()
    
    def generate_stats_report(self):
        """生成统计报告"""
        initial_tokens = self.stats['initial_tokens']
        final_tokens = self.stats['final_tokens']
        
        if initial_tokens > 0:
            removal_percentage = ((initial_tokens - final_tokens) / initial_tokens) * 100
        else:
            removal_percentage = 0
        
        stats_content = f"""# 数据清理统计报告

## 总体统计
- **初始文档数**: {self.stats['initial_docs']}
- **初始Token数**: {initial_tokens:,}
- **最终Token数**: {final_tokens:,}
- **总移除率**: {removal_percentage:.2f}%

## 各步骤详细统计

### 1. 语言检测
- 保留文档数: {self.stats['after_language_detection']}
- 目标语言: {', '.join(self.target_languages)}

### 2. HTML清理
- 清理后文档数: {self.stats['after_html_cleaning']}

### 3. MinHash去重
- 去重后文档数: {self.stats['after_deduplication']}
- 相似度阈值: {self.similarity_threshold}

### 4. PII去除
- 处理后文档数: {self.stats['after_pii_removal']}
- 去除类型: 邮件地址、信用卡号、电话号码、社会安全号

### 5. 重复N-grams去除
- 最终文档数: {self.stats['after_ngram_removal']}

## 清理效果
- **数据质量提升**: 去除了HTML噪声、重复内容、敏感信息
- **去重效果**: 使用MinHash算法有效识别相似文档
- **隐私保护**: 自动检测并移除个人身份信息
- **内容优化**: 减少重复性文本，提高内容质量

## 文件输出
- **clean_corpus.txt**: 清理后的完整语料库
- **stats.md**: 本统计报告

生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open('output/stats.md', 'w', encoding='utf-8') as f:
            f.write(stats_content)
        
        logger.info("统计报告已保存到 output/stats.md")


def main():
    """主函数"""
    # 创建数据清理器
    cleaner = DataCleaner(similarity_threshold=0.7, target_languages=['en', 'zh-cn'])
    
    # 执行清理管道
    clean_documents = cleaner.process_pipeline()
    
    # 保存结果
    cleaner.save_results(clean_documents)
    
    logger.info("数据清理和去重任务完成！")
    logger.info("输出文件:")
    logger.info("- output/clean_corpus.txt")
    logger.info("- output/stats.md")


if __name__ == "__main__":
    main()
