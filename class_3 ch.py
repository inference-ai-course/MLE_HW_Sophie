"""
数据提取与预处理综合示例
本文件演示了机器学习项目中常见的多模态数据提取和预处理技术：
1. 网页文本提取 - 从学术论文网站提取结构化文本
2. 图像OCR - 使用多种方法从图像中提取文字
3. 音频转录 - 将语音转换为文本
4. 数据清理 - 去重、去噪、隐私保护等预处理步骤

适用场景：构建多模态数据集、文档数字化、内容分析等
"""

# =============================================================================
# 第一部分：网页文本提取
# =============================================================================
# 功能：从网页中提取干净的文本内容，去除HTML标签和无关元素
# 应用场景：爬取学术论文摘要、新闻文章、博客内容等用于文本分析

# ✅ 如需要，请先安装依赖项
# !pip install trafilatura

import trafilatura
import requests

# 示例：arXiv论文摘要页面 - 这是机器学习领域最重要的预印本服务器
url = "https://arxiv.org/abs/2404.00001"

# 步骤1：获取原始HTML - 模拟浏览器访问网页
response = requests.get(url)
html = response.text

# 步骤2：使用Trafilatura智能提取文本
# Trafilatura是专门用于网页文本提取的库，能自动识别主要内容区域
# 排除导航栏、广告、评论等干扰信息，保留核心文本内容
downloaded_text = trafilatura.extract(html, include_comments=False, include_tables=False)

# 步骤3：显示提取结果
print("📄 提取的文本预览：\n")
print(downloaded_text[:1000])  # 显示前1000个字符用于预览



# =============================================================================
# 第二部分：传统OCR文字识别
# =============================================================================
# 功能：使用Tesseract引擎从图像中识别文字
# 特点：开源免费，支持多语言，适合处理扫描文档、截图等
# 应用场景：文档数字化、表单处理、图书扫描等

# 安装：sudo apt install tesseract-ocr 或 !pip install pytesseract Pillow
import pytesseract
from PIL import Image

# 图像预处理：转换为灰度图可以提高OCR识别准确率
# 灰度图减少了颜色干扰，让文字轮廓更清晰
image = Image.open("/Users/pc/Documents/cursor/ml course/MLE_in_Gen_AI-Course/Class3/test_data/image/image.png").convert("L")  # 灰度图
text = pytesseract.image_to_string(image)

print("📄 Tesseract OCR输出（前500个字符）：")
print(text[:500])





# =============================================================================
# 第三部分：深度学习OCR - Surya
# =============================================================================
# 功能：使用现代深度学习模型进行OCR，比传统方法更准确
# 特点：提供文字位置坐标和置信度分数，支持复杂布局识别
# 应用场景：复杂文档分析、版面理解、多语言混合文本识别

from PIL import Image
from surya.detection import DetectionPredictor
from surya.recognition import RecognitionPredictor

# 加载待处理图像
image = Image.open("/Users/pc/Documents/cursor/ml course/MLE_in_Gen_AI-Course/Class3/test_data/image/image.png")  # 请替换为您的图像路径
langs = ["en"]  # 指定识别语言，可支持多语言

# 初始化深度学习预测器
# DetectionPredictor：检测文字区域位置
# RecognitionPredictor：识别文字内容
detection_predictor = DetectionPredictor()
recognition_predictor = RecognitionPredictor()

# 执行OCR识别，获取带边界框的文字信息
predictions = recognition_predictor([image], ["ocr_with_boxes"], detection_predictor)



# 输出详细识别结果，包含文字内容、置信度和位置信息
# 这些信息对于文档结构分析和版面重建非常重要
for page in predictions:
    for line in page.text_lines:
        print(f"文本: {line.text}")
        print(f"置信度: {line.confidence}")  # AI模型对识别结果的确信程度
        print(f"多边形: {line.polygon}\n")    # 文字区域的精确坐标




# =============================================================================
# 第四部分：AI视觉模型OCR - GPT-4 Vision
# =============================================================================
# 功能：利用最先进的多模态AI模型进行图像文字识别和理解
# 优势：能理解图像上下文、处理复杂布局、支持自然语言查询
# 应用场景：智能文档理解、表格数据提取、手写文字识别

import base64
import requests

def vision_extract(b64_image, prompt, api_key):
    """
    使用GPT-4视觉模型从图像中提取文本
    
    这种方法的优势：
    1. 理解图像语义和上下文
    2. 可以根据自然语言指令进行定制化提取
    3. 处理复杂布局和非标准格式
    4. 支持多语言混合识别
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",          # 使用轻量级但高效的模型
        "temperature": 0.0,              # 设为0确保结果一致性
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]}
        ],
        "max_tokens": 3000               # 限制响应长度避免超额使用
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

# 图像编码：将图像转换为base64格式供API使用
with open("/Users/pc/Documents/cursor/ml course/MLE_in_Gen_AI-Course/Class3/test_data/image/image.png", "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")

# 调用AI视觉模型进行文字提取
# 注意：API密钥从环境变量读取，确保安全性
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')# Use your actual API key here

if not api_key:
    raise ValueError("请设置OPENAI_API_KEY环境变量")

result = vision_extract(b64_img, "Extract all the readable text from this document.", api_key=api_key)

print(result["choices"][0]["message"]["content"])



# =============================================================================
# 第五部分：音频转录 - OpenAI Whisper
# =============================================================================
# 功能：将音频文件转换为文本，支持多语言语音识别
# 特点：OpenAI开源的最先进语音识别模型，准确率极高
# 应用场景：会议记录、播客转录、多媒体内容分析

# 安装：pip install openai-whisper
import whisper

# 加载Whisper模型
# 模型大小选择：tiny < base < small < medium < large
# 更大的模型准确率更高但处理速度更慢
model = whisper.load_model("base")  # 平衡准确率和速度的选择

# 执行音频转录
# Whisper能自动检测语言、处理噪音、识别多种口音
result = model.transcribe("/Users/pc/Documents/cursor/ml course/practice/week3/test_data/audio/sample-1.mp3")
print("📄 Whisper转录结果：")
print(result["text"])




# =============================================================================
# 第六部分：高效音频转录 - Faster Whisper
# =============================================================================
# 功能：Whisper的优化版本，速度更快且内存占用更少
# 特点：使用量化技术和优化推理，提供时间戳信息
# 适用：大批量音频处理、实时转录需求

from faster_whisper import WhisperModel

# 模型优化配置：使用int8量化减少内存占用并提升速度
# compute_type="int8" 将模型权重从32位压缩到8位，速度提升4-8倍
model = WhisperModel("base", device="cpu", compute_type="int8")  # 适用于CPU环境

# 分段转录：返回带时间戳的文本片段
# 这对于视频字幕生成、会议记录分析非常有用
segments, _ = model.transcribe("/Users/pc/Documents/cursor/ml course/practice/week3/test_data/audio/sample-1.mp3")

print("📄 Faster-Whisper转录结果：")
for segment in segments:
    print(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}")



# =============================================================================
# 第七部分：数据清理与预处理
# =============================================================================
# 目标：将原始文本数据转换为高质量的机器学习训练数据
# 重要性：数据质量直接影响模型性能，清理不当会导致模型学习错误模式

from datasketch import MinHash, MinHashLSH

def minhash_deduplication(texts, threshold=0.7):
    """
    使用MinHash LSH算法进行高效文本去重
    
    工作原理：
    1. 将每个文档转换为MinHash签名（降维表示）
    2. 使用LSH（局部敏感哈希）快速找到相似文档
    3. 只保留唯一文档，去除重复和近似重复内容
    
    优势：处理大规模数据集时比传统方法快数百倍
    应用：避免模型过拟合重复内容，提高训练效率
    """
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    unique_texts = []
    for i, doc in enumerate(texts):
        # 为每个文档生成MinHash签名
        m = MinHash(num_perm=128)
        for word in set(doc.split()):
            m.update(word.encode('utf8'))
        # 检查是否已有相似文档
        if not lsh.query(m):
            lsh.insert(f"doc{i}", m)
            unique_texts.append(doc)
    return unique_texts



from langdetect import detect
from bs4 import BeautifulSoup

def clean_html_and_filter_lang(texts, lang='en'):
    """
    HTML清理和语言过滤功能
    
    功能详解：
    1. 使用BeautifulSoup解析HTML，提取纯文本内容
    2. 移除所有HTML标签、CSS样式、JavaScript代码
    3. 使用langdetect库检测文本语言
    4. 只保留指定语言的文本，确保数据集语言一致性
    
    重要性：网络爬取的数据往往包含大量HTML噪音和多语言混合
    过滤后的数据更适合自然语言处理任务
    """
    filtered = []
    for txt in texts:
        # 解析HTML并提取纯文本
        txt = BeautifulSoup(txt, 'html.parser').get_text()
        try:
            # 检测语言并过滤
            if detect(txt.strip()) == lang:
                filtered.append(txt.strip())
        except:
            # 语言检测失败的文本跳过（通常是内容太短或包含特殊字符）
            continue
    return filtered



import re

def strip_pii(text):
    """
    移除个人身份信息（PII）保护隐私
    
    功能说明：
    - 自动识别并替换敏感信息，防止隐私泄露
    - 使用占位符替换而非删除，保持文本结构完整
    - 这是数据处理的重要合规要求
    
    处理的信息类型：
    1. 邮箱地址 → [EMAIL]
    2. 信用卡号 → [CREDIT_CARD]  
    3. 电话号码 → [PHONE]
    
    扩展建议：可添加身份证号、地址、姓名等其他敏感信息的识别
    """
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', text)  # 匹配邮箱格式
    text = re.sub(r'\b\d{12,19}\b', '[CREDIT_CARD]', text)  # 匹配12-19位数字（信用卡号长度）
    text = re.sub(r'\b(?:\d{3}-){2}\d{4}\b', '[PHONE]', text)  # 匹配XXX-XXX-XXXX格式电话
    return text



import re
from collections import Counter

def remove_repetitive_ngrams(text, n=3, threshold=3):
    """
    移除重复的n-gram短语，提高文本质量
    
    背景问题：
    - 网络爬取的文本常包含重复的广告语、免责声明等
    - 重复内容会影响模型学习，导致生成重复文本
    - 需要智能识别并清理这些重复模式
    
    算法步骤：
    1. 将文本分割为n-gram（默认3个词的组合）
    2. 统计每个n-gram的出现频次
    3. 识别高频重复的短语（超过阈值）
    4. 将连续重复的短语压缩为单次出现
    
    参数调节：
    - n=3: 检测3个词的组合，可根据需要调整
    - threshold=3: 出现3次以上认为是重复，可调整敏感度
    """
    words = text.split()
    # 生成所有n-gram组合
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

    # 统计n-gram频次，识别重复模式
    counts = Counter(ngrams)
    repetitive = [ngram for ngram, count in counts.items() if count >= threshold]

    # 清理重复短语
    for phrase in repetitive:
        # 转义特殊字符以安全用于正则表达式
        escaped_phrase = re.escape(phrase)
        # 将连续重复的短语替换为单次出现
        text = re.sub(rf'(?:{escaped_phrase}\s*){{{threshold},}}', phrase + ' ', text)

    # 标准化空格
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text




# =============================================================================
# 第八部分：完整数据清理流水线演示
# =============================================================================
# 目标：展示如何将原始、混乱的文本数据转换为高质量训练数据
# 这是机器学习项目中最重要但经常被忽视的步骤

import pandas as pd
# 加载示例数据集：模拟真实场景中的原始文本数据
# 这些数据通常包含HTML标签、重复内容、多语言混合、隐私信息等问题
fake_texts = pd.read_csv("/Users/pc/Documents/cursor/ml course/practice/week3/test_data/data/Fake_Pretraining_Texts.csv")
raw_dataset = fake_texts["Raw Text"]
print("原始数据预览:")
print(raw_dataset)

from IPython.display import display

# 数据清理流水线：每一步都解决特定的数据质量问题
print("\n=== 开始数据清理流水线 ===")

# 步骤1：HTML清理 + 语言过滤
# 目的：去除网页标签噪音，确保语言一致性
print("\n步骤1: HTML清理和语言过滤")
step1 = clean_html_and_filter_lang(raw_dataset)
display(step1)

# 步骤2：智能去重
# 目的：移除重复和相似内容，避免模型过拟合
print("\n步骤2: 智能去重处理")
step2 = minhash_deduplication(step1)
display(step2)

# 步骤3：隐私保护
# 目的：移除敏感信息，确保数据使用合规
print("\n步骤3: 隐私信息保护")
step3 = [strip_pii(t) for t in step2]
display(step3)

# 步骤4：去除重复模式
# 目的：清理重复的广告语、模板文本等噪音
print("\n步骤4: 重复模式清理")
cleaned_data = [remove_repetitive_ngrams(t) for t in step3]
display(cleaned_data)

# 流水线完成：展示最终清理结果
print("\n" + "="*50)
print("✅ 数据清理流水线完成！")
print("清理后的高质量数据集：")
for idx, text in enumerate(cleaned_data):
    print(f"\n--- 文章 {idx + 1} ---")
    print(text)

print(f"\n数据统计:")
print(f"原始数据量: {len(raw_dataset)}")
print(f"清理后数据量: {len(cleaned_data)}")
print(f"数据保留率: {len(cleaned_data)/len(raw_dataset)*100:.1f}%")
