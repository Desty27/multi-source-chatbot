import os
import pandas as pd
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

def extract_pdf(file_path):
    reader = PdfReader(file_path)
    extracted_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            extracted_text.append(text.strip())
        else:
            try:
                doc = fitz.open(file_path)
                pix = doc[i].get_pixmap(dpi=300)
                temp_img_path = f"/tmp/page_{i}.png"
                pix.save(temp_img_path)
                img = Image.open(temp_img_path)
                ocr_text = pytesseract.image_to_string(img)
                extracted_text.append(ocr_text.strip() if ocr_text.strip() else "No text found via OCR")
            except Exception as e:
                extracted_text.append(f"OCR error: {str(e)}")
    return extracted_text

def extract_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.astype(str).apply(lambda row: " | ".join(row), axis=1).tolist()
    except Exception as e:
        return [f"Excel error: {str(e)}"]

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return [text] if text.strip() else ["No text found"]
    except Exception as e:
        return [f"OCR error: {str(e)}"]

def handle_upload(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            texts = extract_pdf(file_path)
        elif ext in [".xlsx", ".xls"]:
            texts = extract_excel(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            texts = extract_text_from_image(file_path)
        else:
            return "Unsupported file format"
        return store_data_with_vectors(texts, os.path.basename(file_path))
    except Exception as e:
        return f"Upload error: {str(e)}"