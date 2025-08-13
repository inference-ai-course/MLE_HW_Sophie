#!/usr/bin/env python3
"""
简单的运行脚本，用于快速启动转录任务
Simple runner script for quick transcription tasks
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from transcription_bot import TranscriptionBot, logger

def run_sample_transcription():
    """运行示例转录任务"""
    
    # 示例URL列表（请替换为实际的YouTube视频URL）
    sample_urls = [
        # 这里需要真实的YouTube URL
        # 由于示例URL不可用，用户需要提供真实的视频链接
    ]
    
    if not sample_urls:
        print("请在 sample_urls.txt 文件中添加真实的YouTube视频URL")
        print("或者直接修改 run_transcription.py 中的 sample_urls 列表")
        return
    
    # 创建转录机器人
    output_dir = Path(__file__).parent  # 当前目录
    bot = TranscriptionBot(output_dir=str(output_dir), model_name="base")
    
    try:
        logger.info("开始示例转录任务")
        
        # 处理视频
        bot.process_videos(sample_urls)
        
        # 保存结果
        bot.save_results("talks_transcripts.jsonl")
        
        logger.info("示例转录任务完成！")
        logger.info(f"结果保存在: {output_dir / 'talks_transcripts.jsonl'}")
        
    except Exception as e:
        logger.error(f"转录任务失败: {e}")
    finally:
        # 清理临时文件
        bot.cleanup()

def run_from_file():
    """从文件读取URL并运行转录"""
    urls_file = Path(__file__).parent / "sample_urls.txt"
    
    if not urls_file.exists():
        print(f"URL文件不存在: {urls_file}")
        return
    
    # 读取URL
    urls = []
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and line.startswith('http'):
                    urls.append(line)
    except Exception as e:
        print(f"读取URL文件失败: {e}")
        return
    
    if not urls:
        print("未找到有效的YouTube URL")
        print("请检查 sample_urls.txt 文件")
        return
    
    print(f"找到 {len(urls)} 个URL:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    # 创建转录机器人
    output_dir = Path(__file__).parent
    bot = TranscriptionBot(output_dir=str(output_dir), model_name="base")
    
    try:
        logger.info(f"开始处理 {len(urls)} 个视频")
        
        # 处理视频
        bot.process_videos(urls)
        
        # 保存结果
        bot.save_results("talks_transcripts.jsonl")
        
        logger.info("转录任务完成！")
        
    except Exception as e:
        logger.error(f"转录任务失败: {e}")
    finally:
        # 清理临时文件
        bot.cleanup()

def main():
    """主函数"""
    print("NLP会议演讲转录机器人")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--from-file":
        run_from_file()
    else:
        print("使用方法:")
        print("1. 直接运行: python run_transcription.py --from-file")
        print("2. 使用完整脚本: python transcription_bot.py --urls-file sample_urls.txt")
        print("3. 指定URL: python transcription_bot.py --urls https://youtube.com/watch?v=...")
        print()
        
        choice = input("选择运行方式 (1: 从文件读取URL, 2: 显示帮助): ").strip()
        
        if choice == "1":
            run_from_file()
        else:
            print("\n详细使用说明:")
            print("python transcription_bot.py --help")

if __name__ == "__main__":
    main()
