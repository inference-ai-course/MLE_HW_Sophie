# Automatic Speech Recognition (ASR) Transcription Bot

一个用于NLP会议演讲的自动语音识别转录机器人，使用yt-dlp下载YouTube音频，Whisper进行语音识别，Tesseract进行OCR文本提取。

An Automatic Speech Recognition transcription bot for NLP conference talks, using yt-dlp to fetch YouTube audio, Whisper for transcription, and Tesseract for OCR text extraction.

## 功能特性 (Features)

- 🎥 **YouTube音频下载**: 使用yt-dlp下载高质量音频
- 🗣️ **语音识别**: 基于OpenAI Whisper的准确转录
- 📝 **OCR文本提取**: 从视频帧中提取文本内容（如幻灯片）
- ⏱️ **时间戳支持**: 精确的时间段标记
- 📊 **JSONL输出**: 结构化数据格式，便于后续处理
- 🔄 **批量处理**: 支持同时处理多个视频

## 系统要求 (Requirements)

### Python版本
- Python 3.8+

### 系统依赖
- **FFmpeg**: 音频/视频处理
- **Tesseract OCR**: 光学字符识别

#### macOS安装
```bash
brew install ffmpeg tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install ffmpeg tesseract-ocr
```

### Python依赖包
所有Python依赖包已列在 `requirements.txt` 中。

## 快速开始 (Quick Start)

### 1. 自动安装
```bash
python setup.py
```

### 2. 手动安装
```bash
# 安装Python依赖
pip install -r requirements.txt

# 验证系统依赖
ffmpeg -version
tesseract --version
```

### 3. 准备视频URL
编辑 `sample_urls.txt` 文件，添加要处理的YouTube视频URL:
```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
# ... 更多URL
```

### 4. 运行转录
```bash
# 简单方式
python run_transcription.py --from-file

# 完整命令
python transcription_bot.py --urls-file sample_urls.txt
```

## 使用方法 (Usage)

### 基础用法

#### 处理单个视频
```bash
python transcription_bot.py --urls https://www.youtube.com/watch?v=VIDEO_ID
```

#### 批量处理
```bash
python transcription_bot.py --urls-file sample_urls.txt
```

#### 指定输出目录和模型
```bash
python transcription_bot.py \
  --urls-file sample_urls.txt \
  --output-dir ./output \
  --model medium
```

### 高级选项

#### Whisper模型选择
- `tiny`: 最快，准确性一般
- `base`: 平衡速度和准确性（默认）
- `small`: 更好的准确性
- `medium`: 高准确性
- `large`: 最高准确性，但最慢

#### 命令行参数
```
--urls URL [URL ...]     直接指定YouTube URL列表
--urls-file FILE         从文件读取URL列表
--output-dir DIR         输出文件目录（默认：当前目录）
--model MODEL            Whisper模型大小（默认：base）
--output-file FILE       输出文件名（默认：talks_transcripts.jsonl）
```

## 输出格式 (Output Format)

转录结果保存为JSONL格式，每行一个JSON对象：

```json
{
  "video_id": "talk_01",
  "url": "https://www.youtube.com/watch?v=EXAMPLE",
  "timestamp": "2024-01-15T10:30:00",
  "asr_transcript": {
    "video_id": "talk_01",
    "language": "en",
    "text": "Complete transcript text...",
    "segments": [
      {
        "start": 0.0,
        "end": 3.5,
        "text": "Segment text with timestamps"
      }
    ]
  },
  "ocr_extractions": [
    {
      "image_path": "/tmp/talk_01_frame_0001.png",
      "text": "OCR extracted text from slides",
      "timestamp": "0001"
    }
  ],
  "processing_info": {
    "audio_duration": 180.5,
    "total_segments": 45,
    "total_ocr_extractions": 6
  }
}
```

## 文件结构 (File Structure)

```
.
├── transcription_bot.py      # 主转录脚本
├── run_transcription.py      # 简化运行脚本
├── demo_output.py           # 演示输出格式
├── setup.py                 # 安装脚本
├── requirements.txt         # Python依赖
├── sample_urls.txt          # 示例URL文件
├── README.md               # 文档
├── config.ini              # 配置文件（安装后生成）
├── talks_transcripts.jsonl  # 输出结果（运行后生成）
├── transcription.log       # 日志文件（运行后生成）
└── demo_talks_transcripts.jsonl  # 演示输出（运行demo后生成）
```

## 工作流程 (Workflow)

1. **音频下载**: 使用yt-dlp从YouTube下载音频文件
2. **视频帧提取**: 从视频中提取帧用于OCR处理
3. **语音识别**: 使用Whisper模型转录音频为文本
4. **OCR处理**: 使用Tesseract从视频帧中提取文本
5. **结果合并**: 将ASR和OCR结果合并为结构化格式
6. **输出保存**: 保存为JSONL文件

## 性能优化 (Performance Optimization)

### 硬件建议
- **CPU**: 多核处理器，推荐8核以上
- **内存**: 至少8GB RAM，推荐16GB+
- **GPU**: 支持CUDA的NVIDIA GPU可显著加速Whisper转录
- **存储**: SSD硬盘提升I/O性能

### 优化设置
- 使用较小的Whisper模型（tiny/base）提升速度
- 调整OCR帧提取间隔减少处理量
- 使用GPU加速（需要安装CUDA版本的PyTorch）

## 故障排除 (Troubleshooting)

### 常见问题

#### 1. FFmpeg未找到
```
错误: [Errno 2] No such file or directory: 'ffmpeg'
解决: 安装FFmpeg - brew install ffmpeg (macOS) 或 apt-get install ffmpeg (Linux)
```

#### 2. Tesseract未找到
```
错误: TesseractNotFoundError
解决: 安装Tesseract - brew install tesseract (macOS) 或 apt-get install tesseract-ocr (Linux)
```

#### 3. YouTube下载失败
```
错误: Unable to download YouTube video
解决: 检查网络连接，确认视频URL有效且可访问
```

#### 4. Whisper模型下载缓慢
```
问题: 首次运行时模型下载很慢
解决: 使用较小的模型（tiny/base）或配置代理
```

### 日志调试
查看 `transcription.log` 文件获取详细错误信息：
```bash
tail -f transcription.log
```

## 许可证 (License)

本项目使用MIT许可证。详见LICENSE文件。

## 贡献 (Contributing)

欢迎提交Issue和Pull Request！

## 致谢 (Acknowledgments)

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别模型
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube下载工具
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - 光学字符识别
- [OpenCV](https://opencv.org/) - 计算机视觉库

## 联系方式 (Contact)

如有问题或建议，请通过GitHub Issues联系。
