from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(":memory:")  # Для теста — в памяти


def create_collection(collection_name="default", vector_size=384):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def upload_documents(chunks, vectors, collection_name="gearmotor_docs"):
    points = [
        PointStruct(id=i, vector=vectors[i], payload=chunks[i])
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=collection_name, points=points)


def search_similar(query_vector, collection_name="gearmotor_docs", limit=5):
    return client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )