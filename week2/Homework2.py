
from PIL import Image
import pytesseract #pip install pytesseract first

# Load an image using Pillow (PIL)
image = Image.open('/Users/pc/Downloads/week1234.png')

# Perform OCR on the image
text = pytesseract.image_to_string(image)


print(text)

#Tesseract supports over 100 languages, and you can even train it for custom languages or fonts. To use a different language, you can download the corresponding trained data files and specify the language in the -l flag.
#For example, to use Spanish (spa):
#tesseract /Users/pc/Downloads/week1234.png output -l spa

text = pytesseract.image_to_string(image, lang='spa')  # 指定西班牙语

print(text)