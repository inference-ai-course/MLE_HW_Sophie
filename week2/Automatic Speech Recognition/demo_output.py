#!/usr/bin/env python3
"""
演示脚本 - 生成示例输出格式
Demo script - Generate sample output format
"""

import json
from datetime import datetime
from pathlib import Path

def create_demo_output():
    """创建演示输出文件，显示期望的JSONL格式"""
    
    # 示例转录数据
    sample_transcripts = [
        {
            "video_id": "talk_01",
            "url": "https://www.youtube.com/watch?v=EXAMPLE1",
            "timestamp": "2024-01-15T10:30:00",
            "asr_transcript": {
                "video_id": "talk_01",
                "language": "en",
                "text": "Hello everyone, welcome to today's presentation on transformer architectures. In this talk, we'll explore the attention mechanism and its applications in natural language processing.",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 3.5,
                        "text": "Hello everyone, welcome to today's presentation on transformer architectures."
                    },
                    {
                        "start": 3.5,
                        "end": 8.2,
                        "text": "In this talk, we'll explore the attention mechanism and its applications in natural language processing."
                    },
                    {
                        "start": 8.2,
                        "end": 12.1,
                        "text": "The transformer model has revolutionized the field of machine learning."
                    }
                ]
            },
            "ocr_extractions": [
                {
                    "image_path": "/tmp/talk_01_frame_0001.png",
                    "text": "Transformer Architecture\n• Self-Attention Mechanism\n• Multi-Head Attention\n• Position Encoding",
                    "timestamp": "0001"
                },
                {
                    "image_path": "/tmp/talk_01_frame_0002.png", 
                    "text": "Applications in NLP\n• Machine Translation\n• Text Summarization\n• Question Answering",
                    "timestamp": "0002"
                }
            ],
            "processing_info": {
                "audio_duration": 180.5,
                "total_segments": 45,
                "total_ocr_extractions": 6
            }
        },
        {
            "video_id": "talk_02",
            "url": "https://www.youtube.com/watch?v=EXAMPLE2",
            "timestamp": "2024-01-15T10:45:00",
            "asr_transcript": {
                "video_id": "talk_02", 
                "language": "en",
                "text": "Today we're discussing BERT and the importance of pre-training in language models. BERT uses bidirectional training to better understand context.",
                "segments": [
                    {
                        "start": 0.0,
                        "end": 4.2,
                        "text": "Today we're discussing BERT and the importance of pre-training in language models."
                    },
                    {
                        "start": 4.2,
                        "end": 8.7,
                        "text": "BERT uses bidirectional training to better understand context."
                    },
                    {
                        "start": 8.7,
                        "end": 13.1,
                        "text": "This approach has shown significant improvements in various NLP tasks."
                    }
                ]
            },
            "ocr_extractions": [
                {
                    "image_path": "/tmp/talk_02_frame_0001.png",
                    "text": "BERT: Bidirectional Encoder Representations from Transformers\n• Masked Language Modeling\n• Next Sentence Prediction",
                    "timestamp": "0001"
                }
            ],
            "processing_info": {
                "audio_duration": 175.3,
                "total_segments": 42,
                "total_ocr_extractions": 4
            }
        }
    ]
    
    # 保存到JSONL文件
    output_file = Path(__file__).parent / "demo_talks_transcripts.jsonl"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for transcript in sample_transcripts:
            f.write(json.dumps(transcript, ensure_ascii=False, indent=None) + '\n')
    
    print(f"演示输出文件已创建: {output_file}")
    print(f"包含 {len(sample_transcripts)} 条示例转录记录")
    
    # 显示文件内容预览
    print("\n文件内容预览:")
    print("-" * 50)
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            data = json.loads(line)
            print(f"记录 {i}:")
            print(f"  视频ID: {data['video_id']}")
            print(f"  语言: {data['asr_transcript']['language']}")
            print(f"  转录文本: {data['asr_transcript']['text'][:100]}...")
            print(f"  时间段数: {data['processing_info']['total_segments']}")
            print(f"  OCR提取数: {data['processing_info']['total_ocr_extractions']}")
            print()

def show_usage_examples():
    """显示使用示例"""
    print("使用示例:")
    print("=" * 50)
    
    examples = [
        {
            "description": "处理单个视频",
            "command": "python transcription_bot.py --urls https://www.youtube.com/watch?v=VIDEO_ID"
        },
        {
            "description": "从文件批量处理",
            "command": "python transcription_bot.py --urls-file sample_urls.txt"
        },
        {
            "description": "指定输出目录和模型",
            "command": "python transcription_bot.py --urls-file sample_urls.txt --output-dir ./output --model medium"
        },
        {
            "description": "使用简化脚本",
            "command": "python run_transcription.py --from-file"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}:")
        print(f"   {example['command']}")
        print()

def main():
    """主函数"""
    print("ASR转录机器人 - 演示输出")
    print("=" * 50)
    
    # 创建演示输出
    create_demo_output()
    
    print()
    
    # 显示使用示例
    show_usage_examples()
    
    print("注意事项:")
    print("• 需要先安装依赖: python setup.py")
    print("• 需要提供真实的YouTube视频URL")
    print("• 确保网络连接正常，可以访问YouTube")
    print("• 首次运行会下载Whisper模型，可能需要一些时间")

if __name__ == "__main__":
    main()
