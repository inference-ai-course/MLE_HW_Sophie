#!/usr/bin/env python3
"""
自动语音识别系统 - NLP会议演讲转录机器人
使用 yt-dlp 下载YouTube音频，Whisper进行语音识别，Tesseract进行OCR文本提取
"""

import os
import json
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime

try:
    import yt_dlp
    import whisper
    import cv2
    import pytesseract
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"缺少必要的依赖包: {e}")
    print("请安装: pip install yt-dlp openai-whisper opencv-python pytesseract pillow")
    exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcription.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TranscriptionBot:
    """NLP会议演讲转录机器人"""
    
    def __init__(self, output_dir: str = ".", model_name: str = "base"):
        """
        初始化转录机器人
        
        Args:
            output_dir: 输出文件目录
            model_name: Whisper模型名称 (tiny, base, small, medium, large)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 加载Whisper模型
        logger.info(f"加载Whisper模型: {model_name}")
        self.whisper_model = whisper.load_model(model_name)
        
        # 创建临时文件目录
        self.temp_dir = Path(tempfile.mkdtemp())
        logger.info(f"临时文件目录: {self.temp_dir}")
        
        # 存储转录结果
        self.transcripts = []
    
    def download_audio(self, url: str, video_id: Optional[str] = None) -> str:
        """
        使用yt-dlp下载YouTube音频
        
        Args:
            url: YouTube视频URL
            video_id: 可选的视频ID，用于文件命名
            
        Returns:
            下载的音频文件路径
        """
        if not video_id:
            video_id = url.split('/')[-1].split('?')[0]
        
        audio_path = self.temp_dir / f"{video_id}.wav"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.temp_dir / f"{video_id}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '16000'  # 16kHz采样率，适合语音识别
            ],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"下载音频: {url}")
                ydl.download([url])
                
            if audio_path.exists():
                logger.info(f"音频下载成功: {audio_path}")
                return str(audio_path)
            else:
                raise FileNotFoundError(f"音频文件未找到: {audio_path}")
                
        except Exception as e:
            logger.error(f"音频下载失败: {e}")
            raise
    
    def extract_frames(self, video_url: str, video_id: str, interval: int = 30) -> List[str]:
        """
        从视频中提取帧用于OCR
        
        Args:
            video_url: 视频URL
            video_id: 视频ID
            interval: 提取帧的间隔（秒）
            
        Returns:
            提取的图像文件路径列表
        """
        video_path = self.temp_dir / f"{video_id}_video.mp4"
        
        # 下载视频文件
        ydl_opts = {
            'format': 'best[height<=480]',
            'outtmpl': str(video_path),
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"下载视频用于帧提取: {video_url}")
                ydl.download([video_url])
            
            # 使用OpenCV提取帧
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * interval)
            
            frame_paths = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_path = self.temp_dir / f"{video_id}_frame_{frame_count//frame_interval:04d}.png"
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))
                    logger.info(f"提取帧: {frame_path}")
                
                frame_count += 1
            
            cap.release()
            logger.info(f"总共提取 {len(frame_paths)} 帧")
            return frame_paths
            
        except Exception as e:
            logger.error(f"帧提取失败: {e}")
            return []
    
    def ocr_text_extraction(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        使用Tesseract进行OCR文本提取
        
        Args:
            image_paths: 图像文件路径列表
            
        Returns:
            OCR提取的文本信息列表
        """
        ocr_results = []
        
        for image_path in image_paths:
            try:
                # 读取图像
                image = cv2.imread(image_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # 图像预处理提高OCR准确性
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                gray = cv2.medianBlur(gray, 3)
                
                # 使用Tesseract进行OCR
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(gray, config=custom_config, lang='eng')
                
                if text.strip():
                    ocr_results.append({
                        'image_path': image_path,
                        'text': text.strip(),
                        'timestamp': os.path.basename(image_path).split('_')[-1].split('.')[0]
                    })
                    logger.info(f"OCR提取文本: {image_path} -> {len(text.strip())} 字符")
                
            except Exception as e:
                logger.error(f"OCR处理失败 {image_path}: {e}")
        
        return ocr_results
    
    def transcribe_audio(self, audio_path: str, video_id: str) -> Dict[str, Any]:
        """
        使用Whisper进行音频转录
        
        Args:
            audio_path: 音频文件路径
            video_id: 视频ID
            
        Returns:
            转录结果字典
        """
        try:
            logger.info(f"开始转录音频: {audio_path}")
            result = self.whisper_model.transcribe(audio_path, verbose=True)
            
            # 格式化转录结果
            transcript = {
                'video_id': video_id,
                'language': result.get('language', 'unknown'),
                'text': result['text'],
                'segments': []
            }
            
            # 添加时间戳信息
            for segment in result.get('segments', []):
                transcript['segments'].append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
            
            logger.info(f"转录完成: {video_id}, 检测语言: {transcript['language']}")
            return transcript
            
        except Exception as e:
            logger.error(f"音频转录失败: {e}")
            raise
    
    def process_video(self, url: str, video_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理单个视频：下载音频、转录、OCR提取
        
        Args:
            url: YouTube视频URL
            video_id: 可选的视频ID
            
        Returns:
            完整的处理结果
        """
        if not video_id:
            video_id = url.split('/')[-1].split('?')[0]
        
        logger.info(f"开始处理视频: {video_id}")
        
        # 下载音频并转录
        audio_path = self.download_audio(url, video_id)
        transcript = self.transcribe_audio(audio_path, video_id)
        
        # 提取视频帧并进行OCR
        frame_paths = self.extract_frames(url, video_id)
        ocr_results = self.ocr_text_extraction(frame_paths)
        
        # 合并结果
        result = {
            'video_id': video_id,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'asr_transcript': transcript,
            'ocr_extractions': ocr_results,
            'processing_info': {
                'audio_duration': len(transcript['segments']) > 0 and transcript['segments'][-1]['end'] or 0,
                'total_segments': len(transcript['segments']),
                'total_ocr_extractions': len(ocr_results)
            }
        }
        
        logger.info(f"视频处理完成: {video_id}")
        return result
    
    def process_videos(self, urls: List[str]) -> None:
        """
        批量处理多个视频
        
        Args:
            urls: YouTube视频URL列表
        """
        logger.info(f"开始批量处理 {len(urls)} 个视频")
        
        for i, url in enumerate(urls, 1):
            try:
                video_id = f"talk_{i:02d}"
                logger.info(f"处理第 {i}/{len(urls)} 个视频: {url}")
                
                result = self.process_video(url, video_id)
                self.transcripts.append(result)
                
                logger.info(f"视频 {video_id} 处理成功")
                
            except Exception as e:
                logger.error(f"视频处理失败 {url}: {e}")
                # 继续处理下一个视频
                continue
        
        logger.info(f"批量处理完成，成功处理 {len(self.transcripts)} 个视频")
    
    def save_results(self, output_file: str = "talks_transcripts.jsonl") -> None:
        """
        保存转录结果到JSONL文件
        
        Args:
            output_file: 输出文件名
        """
        output_path = self.output_dir / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for transcript in self.transcripts:
                    f.write(json.dumps(transcript, ensure_ascii=False) + '\n')
            
            logger.info(f"结果已保存到: {output_path}")
            logger.info(f"总共保存 {len(self.transcripts)} 条转录记录")
            
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
            raise
    
    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("临时文件清理完成")
        except Exception as e:
            logger.warning(f"临时文件清理失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NLP会议演讲转录机器人')
    parser.add_argument('--urls', nargs='+', help='YouTube视频URL列表')
    parser.add_argument('--urls-file', help='包含URL的文本文件')
    parser.add_argument('--output-dir', default='.', help='输出文件目录')
    parser.add_argument('--model', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper模型大小')
    parser.add_argument('--output-file', default='talks_transcripts.jsonl', help='输出文件名')
    
    args = parser.parse_args()
    
    # 获取URL列表
    urls = []
    if args.urls:
        urls.extend(args.urls)
    
    if args.urls_file:
        try:
            with open(args.urls_file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])
        except FileNotFoundError:
            logger.error(f"URL文件未找到: {args.urls_file}")
            return
    
    if not urls:
        logger.error("请提供YouTube视频URL")
        parser.print_help()
        return
    
    # 创建转录机器人
    bot = TranscriptionBot(output_dir=args.output_dir, model_name=args.model)
    
    try:
        # 处理视频
        bot.process_videos(urls)
        
        # 保存结果
        bot.save_results(args.output_file)
        
        logger.info("所有任务完成！")
        
    except KeyboardInterrupt:
        logger.info("用户中断执行")
    except Exception as e:
        logger.error(f"执行失败: {e}")
    finally:
        # 清理临时文件
        bot.cleanup()

if __name__ == "__main__":
    main()
