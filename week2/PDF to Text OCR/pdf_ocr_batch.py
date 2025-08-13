#!/usr/bin/env python3
"""
PDF to Text OCR Batch Processor
批量处理PDF文件，使用Tesseract OCR转换为文本
"""

import os
import sys
from pathlib import Path
import argparse
from typing import List, Optional
import logging
from datetime import datetime

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: Required library not installed. Please run: pip install -r requirements.txt")
    print(f"Missing: {e}")
    sys.exit(1)

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_processing.log'),
        logging.StreamHandler()
    ]
)

class PDFOCRProcessor:
    """PDF OCR处理器类"""
    
    def __init__(self, output_dir: str = "pdf_ocr", dpi: int = 300):
        """
        初始化OCR处理器
        
        Args:
            output_dir: 输出目录
            dpi: PDF转图像的分辨率
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.dpi = dpi
        
        # 验证Tesseract是否已安装
        try:
            pytesseract.get_tesseract_version()
            logging.info("Tesseract OCR is available")
        except Exception as e:
            logging.error(f"Tesseract not found: {e}")
            raise
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        预处理图像以提高OCR准确性
        
        Args:
            image: PIL图像对象
            
        Returns:
            预处理后的图像
        """
        # 转换为numpy数组
        img_array = np.array(image)
        
        # 转换为灰度图
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        # 应用高斯模糊去噪
        denoised = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # 自适应阈值处理
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return Image.fromarray(thresh)
    
    def extract_text_from_image(self, image: Image.Image, page_num: int) -> str:
        """
        从图像中提取文本，保持布局结构
        
        Args:
            image: PIL图像对象
            page_num: 页码
            
        Returns:
            提取的文本
        """
        try:
            # 预处理图像
            processed_image = self.preprocess_image(image)
            
            # 使用Tesseract OCR配置来保持布局
            # PSM 6: 假设是单个统一的文本块
            # PSM 12: 稀疏文本，按顺序查找尽可能多的文本，没有特定布局
            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            
            text = pytesseract.image_to_string(
                processed_image, 
                config=custom_config,
                lang='eng'
            )
            
            return text
            
        except Exception as e:
            logging.error(f"Error extracting text from page {page_num}: {e}")
            return f"[Error processing page {page_num}: {e}]\n"
    
    def process_pdf(self, pdf_path: Path) -> bool:
        """
        处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            处理是否成功
        """
        try:
            logging.info(f"Processing: {pdf_path.name}")
            
            # 转换PDF为图像
            pages = convert_from_path(
                pdf_path, 
                dpi=self.dpi,
                fmt='jpeg'
            )
            
            if not pages:
                logging.warning(f"No pages found in {pdf_path.name}")
                return False
            
            # 输出文件路径
            output_file = self.output_dir / f"{pdf_path.stem}.txt"
            
            all_text = []
            all_text.append(f"OCR处理结果 - {pdf_path.name}")
            all_text.append(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            all_text.append(f"总页数: {len(pages)}")
            all_text.append("=" * 80)
            all_text.append("")
            
            # 处理每一页
            for page_num, page in enumerate(pages, 1):
                logging.info(f"Processing page {page_num}/{len(pages)}")
                
                # 添加页面标题
                all_text.append(f"\n--- 第 {page_num} 页 ---\n")
                
                # 提取文本
                text = self.extract_text_from_image(page, page_num)
                
                if text.strip():
                    all_text.append(text)
                else:
                    all_text.append(f"[页面 {page_num} 无可识别文本]")
                
                # 添加页面分隔符
                all_text.append("\n" + "-" * 50 + "\n")
            
            # 保存结果
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))
            
            logging.info(f"Successfully processed {pdf_path.name} -> {output_file.name}")
            return True
            
        except Exception as e:
            logging.error(f"Error processing {pdf_path.name}: {e}")
            return False
    
    def batch_process(self, pdf_directory: Path) -> dict:
        """
        批量处理PDF文件
        
        Args:
            pdf_directory: 包含PDF文件的目录
            
        Returns:
            处理结果统计
        """
        if not pdf_directory.exists():
            logging.error(f"Directory not found: {pdf_directory}")
            return {"error": "Directory not found"}
        
        # 查找所有PDF文件
        pdf_files = list(pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            logging.warning(f"No PDF files found in {pdf_directory}")
            return {"error": "No PDF files found"}
        
        logging.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = {
            "total": len(pdf_files),
            "successful": 0,
            "failed": 0,
            "failed_files": []
        }
        
        # 处理每个PDF文件
        for pdf_file in pdf_files:
            if self.process_pdf(pdf_file):
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["failed_files"].append(pdf_file.name)
        
        return results

def download_arxiv_pdfs(output_dir: Path = Path("pdfs")) -> bool:
    """
    下载arXiv示例PDF文件用于测试
    
    Args:
        output_dir: 输出目录
        
    Returns:
        下载是否成功
    """
    import urllib.request
    
    # 一些示例arXiv论文ID
    sample_papers = [
        "2301.07041",  # GPT相关论文
        "1706.03762",  # Attention is All You Need
        "2005.14165"   # GPT-3论文
    ]
    
    output_dir.mkdir(exist_ok=True)
    success_count = 0
    
    for paper_id in sample_papers:
        try:
            url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            output_file = output_dir / f"{paper_id}.pdf"
            
            if output_file.exists():
                logging.info(f"File already exists: {output_file.name}")
                success_count += 1
                continue
                
            logging.info(f"Downloading {paper_id}...")
            urllib.request.urlretrieve(url, output_file)
            logging.info(f"Downloaded: {output_file.name}")
            success_count += 1
            
        except Exception as e:
            logging.error(f"Failed to download {paper_id}: {e}")
    
    return success_count > 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量PDF OCR处理工具")
    parser.add_argument(
        "--input", "-i", 
        type=str, 
        default="pdfs",
        help="输入PDF文件目录 (默认: pdfs)"
    )
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default="pdf_ocr",
        help="输出文本文件目录 (默认: pdf_ocr)"
    )
    parser.add_argument(
        "--dpi", 
        type=int, 
        default=300,
        help="PDF转图像分辨率 (默认: 300)"
    )
    parser.add_argument(
        "--download", 
        action="store_true",
        help="下载示例arXiv PDF文件"
    )
    
    args = parser.parse_args()
    
    # 如果指定下载示例文件
    if args.download:
        logging.info("Downloading sample arXiv PDFs...")
        if download_arxiv_pdfs(Path(args.input)):
            logging.info("Sample PDFs downloaded successfully")
        else:
            logging.error("Failed to download sample PDFs")
            return
    
    # 创建OCR处理器
    processor = PDFOCRProcessor(args.output, args.dpi)
    
    # 批量处理PDF文件
    input_dir = Path(args.input)
    results = processor.batch_process(input_dir)
    
    if "error" in results:
        logging.error(f"Processing failed: {results['error']}")
        return
    
    # 输出处理结果
    logging.info("=" * 60)
    logging.info("处理结果统计:")
    logging.info(f"总文件数: {results['total']}")
    logging.info(f"成功处理: {results['successful']}")
    logging.info(f"处理失败: {results['failed']}")
    
    if results['failed_files']:
        logging.warning(f"失败文件: {', '.join(results['failed_files'])}")
    
    logging.info(f"文本文件已保存到: {args.output}/")

if __name__ == "__main__":
    main()
