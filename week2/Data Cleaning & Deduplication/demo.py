#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清理和去重管道演示脚本
"""

from main import DataCleaner

def demo_with_custom_data():
    """使用自定义数据演示清理管道"""
    
    # 自定义测试数据
    custom_docs = [
        "<html><body><h1>机器学习课程</h1><p>联系我们：ml@university.edu 或拨打 (555) 123-4567</p></body></html>",
        "This is an English document about machine learning and data processing.",
        "<div><p>Another document with HTML tags and phone: 555-987-6543</p></div>",
        "Esta es una oración en español que debería ser filtrada.",
        "This is an English document about machine learning and data processing.",  # 重复
        "Machine learning is fascinating. Machine learning is fascinating. Machine learning is fascinating.",  # 重复n-grams
        "Credit card: 4532-1234-5678-9012 should be removed for privacy.",
        "这是另一个中文文档，用于测试中文语言检测功能。",
        "Clean unique content for testing purposes."
    ]
    
    print("=== 数据清理和去重管道演示 ===\n")
    print(f"输入数据: {len(custom_docs)} 个文档")
    
    # 创建清理器
    cleaner = DataCleaner(similarity_threshold=0.8, target_languages=['en', 'zh-cn'])
    
    # 运行清理管道
    cleaned_docs = cleaner.process_pipeline(custom_docs)
    
    print(f"\n清理后: {len(cleaned_docs)} 个文档")
    print("\n=== 清理后的文档内容 ===")
    for i, doc in enumerate(cleaned_docs, 1):
        print(f"{i}: {doc}")
    
    print(f"\n=== 详细统计 ===")
    print(f"初始Token数: {cleaner.stats['initial_tokens']}")
    print(f"最终Token数: {cleaner.stats['final_tokens']}")
    print(f"移除率: {((cleaner.stats['initial_tokens'] - cleaner.stats['final_tokens']) / cleaner.stats['initial_tokens']) * 100:.2f}%")

if __name__ == "__main__":
    demo_with_custom_data()
