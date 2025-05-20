from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from werkzeug.utils import secure_filename
import os
from config import COLLECTION_NAME, model, UPLOAD_FOLDER
from db import get_products_by_ids
from extract_tables import extract_table_data
from qdrant_client_setup import search_similar
from utils import extract_text_from_image, init

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/search', methods=['GET'])
def search():
    """
    Поиск моделей по векторному запросу
    ---
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Запрос для поиска
    responses:
      200:
        description: Результаты поиска
    """
    query = request.args.get('q', '')
    query_vector = model.encode(query).tolist()
    results = search_similar(query_vector, collection_name=COLLECTION_NAME, limit=5)

    matched_ids = [res.id for res in results if "model" in res.payload]

    if not matched_ids:
        return jsonify({"success": False, "error": "Подходящих моделей не найдено."}), 400

    products = get_products_by_ids(matched_ids)

    return jsonify([
        {"id": pid, "model": model_name}
        for pid, model_name in products
    ])


@app.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Загрузка PDF и извлечение моделей
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: PDF файл
    responses:
      200:
        description: Успешная загрузка и парсинг
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            count:
              type: integer
              example: 15
            message:
              type: string
              example: "Файл успешно обработан"
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Пустое имя файла'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    parsed = extract_table_data(filepath)
    return jsonify({
        "message": "Файл успешно загружен и обработан",
        "items_extracted": len(parsed)
    })


@app.route("/upload-image", methods=["POST"])
def upload_image():
    """
        Распознавание текста с изображения
        ---
        consumes:
          - multipart/form-data
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: Изображение (JPEG/PNG)
        responses:
          200:
            description: Успешное распознавание
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                query:
                  type: string
                  example: "Модель C213, P1N: 2.3, T2N: 210"
        """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    try:
        texts = extract_text_from_image(file)
        query = " ".join(texts)
        return jsonify({"success": True, "query": query, "parts": texts}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    init()
    app.run(debug=True)

    # редуктор с передаточным числом 5.6
    # мотор мощностью 2.2 кВт
    # mounting position D1
    # TODO Прикрутить лучше поиск по моделям
    # TODO Прикрутить загрузку новых pdf через flask
    # TODO Доделать ❌ Подходящих моделей не найдено.
    # TODO Прикрутить поиск по параметрам значений в sqlite
    # TODO FLASK
