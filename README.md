# MLE_HW_Sophie

This repository contains homework assignments for the [Inference AI Course](https://github.com/inference-ai-course). Each week's assignments demonstrate different aspects of machine learning engineering, from LLM integration to computer vision applications.

## Repository Structure

```
├── week1/          # Week 1: LLM Integration with Ollama and LangChain
│   ├── gradio_app.py
│   ├── requirements.txt
│   ├── test_langchain_ollama.py
│   ├── test_ollama_openai.py
│   └── *.png       # Screenshots and examples
├── week2/          # Week 2: Computer Vision - OCR with Tesseract
│   ├── Class 2 Homework.ipynb
│   ├── Homework2.py
│   └── output.txt
```

## Week 1: LLM Integration

### Overview
Week 1 focuses on integrating Large Language Models using Ollama, LangChain, and OpenAI-compatible APIs. The main deliverable is a Gradio web application that provides two interfaces for AI interaction.

### Features
- **🌍 Capital Query (LangChain)**: Uses LangChain framework to query country capitals
- **💬 Intelligent Assistant (OpenAI API)**: Chat interface with conversation history using OpenAI-compatible API

### Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull required model
ollama pull llama2
```

### Installation
```bash
cd week1
pip install -r requirements.txt
```

### Usage
```bash
python gradio_app.py
```

Access the web interface at: `http://localhost:7860`

### Technical Stack
- **Frontend**: Gradio
- **Backend**: LangChain + OpenAI Client
- **Model**: Ollama (llama2)
- **APIs**: OpenAI-compatible REST API

## Week 2: Computer Vision - OCR

### Overview
Week 2 explores Optical Character Recognition (OCR) using Tesseract OCR engine with Python. The assignment demonstrates text extraction from images with multi-language support.

### Features
- Image text extraction using Tesseract OCR
- Multi-language support (English, Spanish, etc.)
- PIL (Pillow) integration for image processing

### Prerequisites
```bash
# Install Tesseract OCR
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Installation
```bash
cd week2
pip install pillow pytesseract
```

### Usage
```bash
python Homework2.py
```

Or run the Jupyter notebook:
```bash
jupyter notebook "Class 2 Homework.ipynb"
```

## Course Information

This repository is part of the homework assignments for the **Inference AI Course**. The course covers various aspects of machine learning engineering including:

- LLM Integration and API Usage
- Computer Vision Applications
- AI Model Deployment
- Machine Learning Pipeline Development

## Course Repository
Main course materials: [https://github.com/inference-ai-course](https://github.com/inference-ai-course)

## Author
**Sophie Zhang** - Course Participant

## License
This repository is for educational purposes as part of the Inference AI Course homework assignments.

---

### 📝 Notes
- Each week's assignments are self-contained with their own requirements
- Screenshots and examples are included for reference
- All code includes Chinese comments as per course requirements
- Make sure all prerequisites are installed before running the applications

### 🚀 Quick Start
1. Clone this repository
2. Navigate to the desired week's directory
3. Install requirements: `pip install -r requirements.txt`
4. Follow the specific setup instructions for each week
5. Run the applications as described in each section
