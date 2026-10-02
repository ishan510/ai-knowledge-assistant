from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient, models

from ingest import PROJECT_DIR
from index_vectors import COLLECTION, DATABASE_PATH


def search(question, top_k=10):
    if not question.strip():
        raise ValueError("Please enter a question.")
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run index_vectors.py first.")

    load_dotenv(PROJECT_DIR / ".env")
    database = QdrantClient(path=str(DATABASE_PATH))

    try:
        if not database.collection_exists(COLLECTION):
            raise ValueError("Knowledge collection is missing.")

        # Read the embedding model from an indexed record.
        sample, _ = database.scroll(
            collection_name=COLLECTION,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not sample:
            raise ValueError("The knowledge collection is empty.")

        model = sample[0].payload["embedding_model"]

        client = OpenAI()
        response = client.embeddings.create(
            model=model,
            input=question,
        )
        question_vector = response.data[0].embedding

        # Retrieve the most similar sections.
        hits = database.query_points(
            collection_name=COLLECTION,
            query=question_vector,
            limit=top_k,
            with_payload=True,
        ).points

        if not hits:
            return []

        # Include all sections from the highest-ranked document.
        primary_source = hits[0].payload["source"]
        source_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source",
                    match=models.MatchValue(value=primary_source),
                )
            ]
        )

        section_count = database.count(
            collection_name=COLLECTION,
            count_filter=source_filter,
            exact=True,
        ).count

        related_hits = database.query_points(
            collection_name=COLLECTION,
            query=question_vector,
            query_filter=source_filter,
            limit=section_count,
            with_payload=True,
        ).points

        selected = list(hits)
        selected_ids = {hit.id for hit in selected}

        for hit in related_hits:
            if hit.id not in selected_ids:
                selected.append(hit)
                selected_ids.add(hit.id)

        # Preserve the format expected by answer.py.
        return [
            {
                "id": hit.payload["chunk_id"],
                "source": hit.payload["source"],
                "section": hit.payload["section"],
                "text": hit.payload["text"],
                "score": float(hit.score),
            }
            for hit in selected
        ]

    finally:
        database.close()


if __name__ == "__main__":
    question = input("Ask a question: ").strip()
    results = search(question)

    for rank, result in enumerate(results, start=1):
        print(
            f"\n--- Result {rank} | "
            f"Similarity: {result['score']:.3f} ---"
        )
        print(f"Source: {result['source']}")
        print(f"Section: {result['section']}")
        print(result["text"])