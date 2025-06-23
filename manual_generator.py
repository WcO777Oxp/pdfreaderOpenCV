import os
import re
import numpy as np
import cv2
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image, ImageOps
import pytesseract

POPPLER_PATH = r"./res/poppler/Library/bin"

PDF_RES = "./res"  # Folder where your PDFs are
OUTPUT_DIR = os.path.join("res", "images")  # Save under res/images/PDF_NAME
TOC_SCAN_PAGES = 8

def clean_filename(title):
    name = re.sub(r"[^\w\s-]", "", title).strip().lower().replace(" ", "_")
    name = re.sub(r"_+", "_", name)
    return name + ".png"

def extract_titles_from_toc(text_lines):
    titles = []
    for line in text_lines:
        cleaned_line = line.strip()
        match = re.match(r"^(.*?)\.{2,}|[\s]{2,}(\d{1,3})$", cleaned_line)
        if match:
            title = match.group(1).strip()
            page_match = re.search(r"(\d{1,3})$", cleaned_line)
            if page_match:
                page_num = int(page_match.group(1).strip())
                titles.append((title, page_num))
    return titles

def extract_toc_with_ocr(pdf_path):
    print("Using OCR to extract TOC from first few pages")
    toc_lines = []
    try:
        images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=TOC_SCAN_PAGES, poppler_path=POPPLER_PATH)
        for img in images:
            img = ImageOps.grayscale(img)
            img = ImageOps.autocontrast(img)
            text = pytesseract.image_to_string(img)
            toc_lines.extend(text.splitlines())
    except Exception as e:
        print(f"OCR extraction failed: {e}")
    return extract_titles_from_toc(toc_lines)

# Just a placeholder crop (no OpenCV logic applied here)
def crop_image(image):
    return image  # ← Cropping disabled; OpenCV is imported but not applied

def generate_images_and_insert(pdf_path, output_dir):
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    print(f"Converting PDF pages to images: {pdf_path}")

    try:
        pages = convert_from_path(pdf_path, dpi=200, poppler_path=POPPLER_PATH)
    except Exception as e:
        print(f"ERROR: PDF conversion failed: {e}")
        return []

    reader = PdfReader(pdf_path)
    toc_text = []
    for i in range(min(TOC_SCAN_PAGES, len(reader.pages))):
        try:
            text = reader.pages[i].extract_text()
            if text:
                toc_text.extend(text.splitlines())
        except:
            continue

    section_titles = extract_titles_from_toc(toc_text)
    if not section_titles:
        print("No TOC titles found — using OCR fallback.")
        section_titles = extract_toc_with_ocr(pdf_path)

    if not section_titles:
        print("TOC OCR also failed. Skipping.")
        return []

    for title, page_number in section_titles:
        pdf_index = page_number - 1
        if pdf_index < 0 or pdf_index >= len(pages):
            continue

        image = pages[pdf_index]
        cropped = crop_image(image)  # ← Still using "cropped", but now no cropping
        filename = clean_filename(title)
        image_path = os.path.join(output_dir, filename)

        try:
            cropped.save(image_path)
            print(f"Inserted → {image_path} | Title: {title}")
        except Exception as e:
            print(f"Failed to save image '{filename}': {e}")
            continue

        try:
            page_text = reader.pages[pdf_index].extract_text() or ""
            if page_text:
                text_path = os.path.join(output_dir, filename.replace(".png", ".txt"))
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(page_text.strip())
        except:
            pass

    return []

def run_manual_import():
    pdfs = sorted(f for f in os.listdir(PDF_RES) if f.lower().endswith(".pdf"))
    if not pdfs:
        print("❌ No PDF files found.")
        return []

    skipped = []
    processed = []

    for pdf in pdfs:
        pdf_path = os.path.join(PDF_RES, pdf)
        pdf_name = os.path.splitext(pdf)[0]
        output_dir = os.path.join("res", "images", pdf_name)

        if os.path.exists(output_dir) and len(os.listdir(output_dir)) > 0:
            print(f"⚠️ Skipping already processed: {pdf}")
            skipped.append(pdf)
            continue

        print(f"📘 Converting PDF → {pdf}")
        generate_images_and_insert(pdf_path, output_dir)
        processed.append(pdf)

    print("\n✅ All processing complete.")
    if processed:
        print("📂 Processed PDFs:")
        for p in processed:
            print(f"  • {p}")
    if skipped:
        print("\n⏩ Skipped PDFs (already converted):")
        for s in skipped:
            print(f"  • {s}")
