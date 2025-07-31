#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行arXiv抓取器的主脚本
自动检查和安装依赖项
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """检查并安装必要的依赖项"""
    required_packages = [
        "requests",
        "trafilatura",
        "lxml"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n正在安装缺失的包: {', '.join(missing_packages)}")
        for package in missing_packages:
            print(f"安装 {package}...")
            if install_package(package):
                print(f"✅ {package} 安装成功")
            else:
                print(f"❌ {package} 安装失败")
                return False
    
    return True

def main():
    """主函数"""
    print("=== arXiv抓取器启动脚本 ===\n")
    
    # 检查并安装依赖项
    print("1. 检查依赖项...")
    if not check_and_install_dependencies():
        print("❌ 依赖项安装失败，程序退出")
        return
    
    print("\n2. 启动抓取器...")
    
    # 导入并运行简化版抓取器
    try:
        from arxiv_scraper_simple import main as scraper_main
        scraper_main()
    except ImportError as e:
        print(f"❌ 导入抓取器模块失败: {e}")
        print("请确保 arxiv_scraper_simple.py 文件存在")
    except Exception as e:
        print(f"❌ 运行抓取器时出错: {e}")

if __name__ == "__main__":
    main()
