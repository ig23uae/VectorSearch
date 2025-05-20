import fitz
import json
import re
import os
import pandas as pd


def extract_table_data(pdf_path, save_path="storage/parsed_tables.json"):
    doc = fitz.open(pdf_path)
    result = []
    model_regex = re.compile(r"\bC\d{3}\b")  # Ищем C107, C108 и т.д.

    for page_number in range(len(doc)):
        text = doc[page_number].get_text()
        lines = text.split("\n")

        current_model = None
        for line in lines:
            model_match = model_regex.search(line)
            if model_match:
                current_model = model_match.group()

            match = re.findall(r"(\d{2,4})\s+([0-9.]{1,5})\s+([0-9.]{1,5})", line)
            for (t2n, iex, p1n) in match:
                if current_model:
                    try:
                        result.append({
                            "model": current_model,
                            "page": page_number + 1,
                            "t2n": float(t2n),
                            "iex": float(iex),
                            "p1n": float(p1n),
                            "text": f"{current_model}, iex: {iex}, P1N: {p1n}, T2N: {t2n}"
                        })
                    except ValueError:
                        continue

    # ❗ Удаляем дубликаты по model, t2n, iex, p1n
    df = pd.DataFrame(result)
    df_unique = df.drop_duplicates(subset=["model", "t2n", "iex", "p1n"])
    result = df_unique.to_dict(orient="records")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[✓] Извлечено {len(result)} уникальных строк из таблиц. Сохранено в {save_path}")
    return result
