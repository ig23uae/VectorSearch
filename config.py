from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
COLLECTION_NAME = "gearmotor_vectors"
PDF_PATH = "data/C Helical Gearmotor.pdf"
DATA_PATH = "storage/parsed_tables.json"
UPLOAD_FOLDER = "storage/uploads"
model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient("http://localhost:6333")
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")