# ✅ Install dependencies if not already installed
# !pip install trafilatura

import trafilatura
import requests

# Example: An arXiv paper abstract page
url = "https://arxiv.org/abs/2404.00001"

# Step 1: Fetch raw HTML
response = requests.get(url)
html = response.text

# Step 2: Use Trafilatura to extract clean text
downloaded_text = trafilatura.extract(html, include_comments=False, include_tables=False)

# Step 3: Display the result
print("📄 Extracted Text Preview:\n")
print(downloaded_text[:1000])  # Show first 1000 characters


# Install: sudo apt install tesseract-ocr OR !pip install pytesseract Pillow
import pytesseract
from PIL import Image

# Load and preprocess image (convert to grayscale)
image = Image.open("/Users/pc/Documents/cursor/ml course/MLE_in_Gen_AI-Course/Class3/test_data/image/image.png").convert("L")  # grayscale
text = pytesseract.image_to_string(image)

print("📄 Tesseract OCR Output (first 500 chars):")
print(text[:500])




from PIL import Image
from surya.detection import DetectionPredictor
from surya.recognition import RecognitionPredictor

# Load the image
image = Image.open("/Users/pc/Documents/cursor/ml course/MLE_in_Gen_AI-Course/Class3/test_data/image/image.png")  # Replace with your image path
langs = ["en"]  # Specify the language(s)

# Initialize predictors
detection_predictor = DetectionPredictor()
recognition_predictor = RecognitionPredictor()

# Perform OCR
predictions = recognition_predictor([image], ["ocr_with_boxes"], detection_predictor)



# Display results with polygon coordinates
for page in predictions:
    for line in page.text_lines:
        print(f"Text: {line.text}")
        print(f"Confidence: {line.confidence}")
        print(f"Polygon: {line.polygon}\n")



import base64
import requests

def vision_extract(b64_image, prompt, api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]}
        ],
        "max_tokens": 3000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

# Load image and run GPT-4o OCR
with open("/Users/pc/Documents/cursor/ml course/MLE_in_Gen_AI-Course/Class3/test_data/image/image.png", "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")


from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')# Use your actual API key here

if not api_key:
    raise ValueError("请设置OPENAI_API_KEY环境变量")

result = vision_extract(b64_img, "Extract all the readable text from this document.", api_key=api_key)
print(result["choices"][0]["message"]["content"])


# Install: pip install openai-whisper
import whisper

# Load model
model = whisper.load_model("base")  # or "small", "medium", "large"

# Transcribe audio
result = model.transcribe("/Users/pc/Documents/cursor/ml course/practice/week3/test_data/audio/sample-1.mp3")
print("📄 Whisper Transcription:")
print(result["text"])



from faster_whisper import WhisperModel

# Load model with float16 for speed
model = WhisperModel("base", device="cpu", compute_type="int8")  # For CPUs

# Transcribe
segments, _ = model.transcribe("/Users/pc/Documents/cursor/ml course/practice/week3/test_data/audio/sample-1.mp3")

print("📄 Faster-Whisper Transcription:")
for segment in segments:
    print(f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}")


from datasketch import MinHash, MinHashLSH

def minhash_deduplication(texts, threshold=0.7):
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    unique_texts = []
    for i, doc in enumerate(texts):
        m = MinHash(num_perm=128)
        for word in set(doc.split()):
            m.update(word.encode('utf8'))
        if not lsh.query(m):
            lsh.insert(f"doc{i}", m)
            unique_texts.append(doc)
    return unique_texts


from langdetect import detect
from bs4 import BeautifulSoup

def clean_html_and_filter_lang(texts, lang='en'):
    filtered = []
    for txt in texts:
        txt = BeautifulSoup(txt, 'html.parser').get_text()
        try:
            if detect(txt.strip()) == lang:
                filtered.append(txt.strip())
        except:
            continue
    return filtered


import re

def strip_pii(text):
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', text)
    text = re.sub(r'\b\d{12,19}\b', '[CREDIT_CARD]', text)
    text = re.sub(r'\b(?:\d{3}-){2}\d{4}\b', '[PHONE]', text)
    return text


import re
from collections import Counter

def remove_repetitive_ngrams(text, n=3, threshold=3):
    words = text.split()
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

    counts = Counter(ngrams)
    repetitive = [ngram for ngram, count in counts.items() if count >= threshold]

    for phrase in repetitive:
        # regex-safe version of the phrase
        escaped_phrase = re.escape(phrase)
        # match the phrase repeated 2+ times with optional whitespace
        text = re.sub(rf'(?:{escaped_phrase}\s*){{{threshold},}}', phrase + ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text



import pandas as pd
fake_texts = pd.read_csv("/Users/pc/Documents/cursor/ml course/practice/week3/test_data/data/Fake_Pretraining_Texts.csv")
raw_dataset = fake_texts["Raw Text"]
print(raw_dataset)

from IPython.display import display

# Step 1: Remove HTML + Language Filter
step1 = clean_html_and_filter_lang(raw_dataset)
display(step1)


# Step 2: Deduplicate Paragraphs
step2 = minhash_deduplication(step1)
display(step2)


# Step 3: Strip PII
step3 = [strip_pii(t) for t in step2]
display(step3)


# Step 4: Remove Repetitive N-grams
cleaned_data = [remove_repetitive_ngrams(t) for t in step3]
display(cleaned_data)


# Done!
print("✅ Cleaned dataset sample:")
for idx, text in enumerate(cleaned_data):
    print(f"--- Article {idx + 1} ---")
    print(text)
