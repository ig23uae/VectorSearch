import json
import easyocr
from typing import List, Dict
from db import init_db, insert_product
from extract_tables import extract_table_data
from qdrant_client_setup import create_collection, upload_documents
from qdrant_client.http.models import ScoredPoint
from config import COLLECTION_NAME, DATA_PATH, PDF_PATH, model, encoder, qdrant


def load_data():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return extract_table_data(PDF_PATH, DATA_PATH)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    return model.encode(texts).tolist()


def extract_text_from_image(file) -> List[str]:
    # Прочитать файл как байты
    image_bytes = file.read()

    # Перезапуск EasyOCR каждый раз неэффективен, но допустимо для краткости
    reader = easyocr.Reader(['en'])  # можешь добавить 'ru'

    # Распознать текст
    results = reader.readtext(image_bytes)

    return [text for (_, text, _) in results]


def search_models(query: str, limit: int = 10) -> List[Dict]:
    query_vector = encoder.encode(query).tolist()

    results: List[ScoredPoint] = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )

    return [
        {
            "id": r.id,
            "model": r.payload.get("model"),
            "text": r.payload.get("text"),
            "score": r.score
        }
        for r in results
    ]


def init():
    print("[•] Инициализация БД...")
    init_db()

    print("[•] Загрузка и парсинг таблиц...")
    items = load_data()
    texts = [item["text"] for item in items]

    print("[•] Генерация эмбеддингов...")
    vectors = get_embeddings(texts)

    print("[•] Загрузка в Qdrant...")
    create_collection(collection_name=COLLECTION_NAME)
    upload_documents(items, vectors, collection_name=COLLECTION_NAME)

    print("[•] Сохранение моделей в БД...")
    for item in items:
        insert_product(item["model"], item["text"], item["page"])
