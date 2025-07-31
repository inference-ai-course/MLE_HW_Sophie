# PDF to Text OCR

批量处理arXiv PDF文件，使用Tesseract OCR转换为文本并保持布局结构。

## 功能特点

- 批量处理多个PDF文件
- 使用Tesseract OCR进行高质量文本提取
- 保持原有布局结构（标题、段落、章节）
- 图像预处理提高OCR准确性
- 详细的处理日志和错误报告
- 支持命令行和Jupyter notebook使用

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 还需要安装Tesseract OCR：
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt install tesseract-ocr`
- Windows: 下载安装 https://github.com/UB-Mannheim/tesseract/wiki

## 使用方法

### 命令行使用

```bash
# 基本用法
python pdf_ocr_batch.py

# 下载示例文件并处理
python pdf_ocr_batch.py --download

# 指定输入输出目录
python pdf_ocr_batch.py -i pdfs/ -o pdf_ocr/

# 调整图像质量
python pdf_ocr_batch.py --dpi 600
```

### Jupyter Notebook

打开 `pdf_ocr_demo.ipynb` 查看完整的演示和使用说明。

## 项目结构

```
PDF to Text OCR/
├── pdf_ocr_batch.py      # 主要OCR处理脚本
├── pdf_ocr_demo.ipynb    # Jupyter演示notebook
├── requirements.txt      # Python依赖
├── pdfs/                 # 输入PDF文件目录
├── pdf_ocr/             # 输出文本文件目录
└── README.md            # 项目文档
```

## 输出格式

每个PDF文件会生成对应的.txt文件，包含：
- 文档标题和处理信息
- 按页面分组的文本内容
- 保持原有的段落和布局结构
- 页面分隔符和页码信息

## 配置选项

- `--input`: 输入PDF目录 (默认: pdfs)
- `--output`: 输出文本目录 (默认: pdf_ocr)
- `--dpi`: 图像分辨率 (默认: 300)
- `--download`: 下载示例arXiv论文

## 技术细节

- 使用 `pdf2image` 将PDF转换为图像
- 通过 `cv2` 进行图像预处理和降噪
- 使用 `pytesseract` 进行OCR文本提取
- PSM 6 模式适合学术论文的布局识别
- 支持中英文处理日志
