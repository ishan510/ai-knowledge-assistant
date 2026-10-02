import json
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from ingest import PROJECT_DIR

COLLECTION = "northstar_knowledge"
DATABASE_PATH = PROJECT_DIR / "data" / "qdrant"


def main():
    embeddings_path = PROJECT_DIR / "data" / "embeddings.json"
    saved = json.loads(embeddings_path.read_text(encoding="utf-8"))
    chunks = saved["chunks"]

    if not chunks:
        raise ValueError("No embeddings found.")

    if len({chunk["id"] for chunk in chunks}) != len(chunks):
        raise ValueError("Duplicate chunk IDs found.")

    for chunk in chunks:
        if len(chunk["embedding"]) != saved["dimensions"]:
            raise ValueError(f"Invalid dimensions: {chunk['id']}")

    client = QdrantClient(path=str(DATABASE_PATH))

    try:
        if client.collection_exists(COLLECTION):
            raise RuntimeError(
                "The collection already exists. "
                "Stopped to avoid mixing different data versions."
            )

        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=saved["dimensions"],
                distance=models.Distance.COSINE,
            ),
        )

        points = [
            models.PointStruct(
                id=str(uuid5(NAMESPACE_URL, chunk["id"])),
                vector=chunk["embedding"],
                payload={
                    "chunk_id": chunk["id"],
                    "source": chunk["source"],
                    "section": chunk["section"],
                    "text": chunk["text"],
                    "embedding_model": saved["model"],
                },
            )
            for chunk in chunks
        ]

        client.upsert(
            collection_name=COLLECTION,
            points=points,
            wait=True,
        )

        count = client.count(
            collection_name=COLLECTION,
            exact=True,
        ).count

        if count != len(chunks):
            raise RuntimeError(
                f"Expected {len(chunks)} records, found {count}."
            )

        print(f"Indexed {count} chunks successfully.")
        print(f"Collection: {COLLECTION}")
        print(f"Dimensions: {saved['dimensions']}")
        print(f"Database: {DATABASE_PATH}")

    finally:
        client.close()


if __name__ == "__main__":
    main()