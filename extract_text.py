import fitz
import json
import os
import re

def extract_chunks_from_pdf(pdf_path, save_path="storage/chunks.json"):
    doc = fitz.open(pdf_path)
    chunks = []
    model_regex = re.compile(r"\bC\d{2,4}[A-Z\-]*\b")  # Пример: C308HA-C32-D101-A

    for page_number in range(len(doc)):
        text = doc[page_number].get_text().strip()
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 20]

        for line in lines:
            model_match = model_regex.search(line)
            if model_match:
                chunks.append({
                    "page": page_number + 1,
                    "text": line,
                    "model": model_match.group()
                })

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"[✓] Извлечено {len(chunks)} блоков-моделей из PDF.")
    return chunks
