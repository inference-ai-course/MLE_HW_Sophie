#!/usr/bin/env python3
"""
安装和设置脚本
Installation and setup script for ASR Transcription Bot
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    
    print(f"✓ Python版本检查通过: {sys.version}")
    return True

def check_system_dependencies():
    """检查系统依赖"""
    print("检查系统依赖...")
    
    dependencies = {
        'ffmpeg': 'FFmpeg (音频/视频处理)',
        'tesseract': 'Tesseract OCR (文字识别)',
    }
    
    missing = []
    
    for cmd, desc in dependencies.items():
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {desc}: 已安装")
            else:
                missing.append((cmd, desc))
        except FileNotFoundError:
            missing.append((cmd, desc))
    
    if missing:
        print("\n缺少以下系统依赖:")
        system = platform.system().lower()
        
        for cmd, desc in missing:
            print(f"✗ {desc}")
            
            if system == 'darwin':  # macOS
                if cmd == 'ffmpeg':
                    print(f"  安装命令: brew install ffmpeg")
                elif cmd == 'tesseract':
                    print(f"  安装命令: brew install tesseract")
            elif system == 'linux':
                if cmd == 'ffmpeg':
                    print(f"  安装命令: sudo apt-get install ffmpeg")
                elif cmd == 'tesseract':
                    print(f"  安装命令: sudo apt-get install tesseract-ocr")
            else:
                print(f"  请参考官方文档安装 {cmd}")
        
        return False
    
    return True

def install_python_dependencies():
    """安装Python依赖包"""
    print("安装Python依赖包...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("错误: requirements.txt 文件不存在")
        return False
    
    try:
        # 更新pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # 安装依赖
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], check=True)
        
        print("✓ Python依赖包安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Python依赖包安装失败: {e}")
        return False

def test_installation():
    """测试安装"""
    print("测试安装...")
    
    try:
        # 测试导入关键模块
        import yt_dlp
        import whisper
        import cv2
        import pytesseract
        from PIL import Image
        
        print("✓ 所有Python模块导入成功")
        
        # 测试Whisper模型加载
        print("测试Whisper模型加载...")
        model = whisper.load_model("tiny")
        print("✓ Whisper模型加载成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 安装测试失败: {e}")
        return False

def create_sample_config():
    """创建示例配置文件"""
    config_content = """# ASR转录机器人配置文件
# Configuration file for ASR Transcription Bot

# Whisper模型设置
whisper_model = "base"  # tiny, base, small, medium, large

# 输出设置
output_directory = "."
output_filename = "talks_transcripts.jsonl"

# OCR设置
ocr_enabled = true
frame_extraction_interval = 30  # 每30秒提取一帧

# 日志设置
log_level = "INFO"
log_file = "transcription.log"
"""
    
    config_file = Path(__file__).parent / "config.ini"
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✓ 创建配置文件: {config_file}")

def main():
    """主安装流程"""
    print("ASR转录机器人 - 安装脚本")
    print("=" * 50)
    
    # 1. 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # 2. 检查系统依赖
    if not check_system_dependencies():
        print("\n请先安装缺少的系统依赖，然后重新运行此脚本")
        sys.exit(1)
    
    print()
    
    # 3. 安装Python依赖
    if not install_python_dependencies():
        sys.exit(1)
    
    print()
    
    # 4. 测试安装
    if not test_installation():
        print("安装测试失败，请检查错误信息")
        sys.exit(1)
    
    print()
    
    # 5. 创建示例配置
    create_sample_config()
    
    print()
    print("🎉 安装完成!")
    print()
    print("使用方法:")
    print("1. 编辑 sample_urls.txt 文件，添加YouTube视频URL")
    print("2. 运行: python run_transcription.py --from-file")
    print("3. 或使用完整命令: python transcription_bot.py --urls-file sample_urls.txt")
    print()
    print("输出文件: talks_transcripts.jsonl")

if __name__ == "__main__":
    main()
