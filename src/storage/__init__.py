import os

import dotenv

from src.storage.minio_client import MinioClient

dotenv.load_dotenv()

minio_client = MinioClient(
    endpoint=os.getenv("MINIO_ENDPOINT", ""),
    access_key=os.getenv("MINIO_ACCESS_KEY", ""),
    secret_key=os.getenv("MINIO_SECRET_KEY", ""),
)
