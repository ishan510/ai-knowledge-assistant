import json
import math

from dotenv import load_dotenv
from openai import OpenAI

from ingest import PROJECT_DIR


def cosine_similarity(first, second):
    if len(first) != len(second):
        raise ValueError("Embedding dimensions do not match.")

    dot_product = sum(a * b for a, b in zip(first, second))
    first_length = math.sqrt(sum(a * a for a in first))
    second_length = math.sqrt(sum(b * b for b in second))

    if first_length == 0 or second_length == 0:
        return 0.0

    return dot_product / (first_length * second_length)


def search(question, top_k=10):
    if not question.strip():
        raise ValueError("Please enter a question.")

    load_dotenv(PROJECT_DIR / ".env")
    client = OpenAI()

    embeddings_path = PROJECT_DIR / "data" / "embeddings.json"
    saved_data = json.loads(
        embeddings_path.read_text(encoding="utf-8")
    )

    # Questions must use the same embedding model as the documents.
    response = client.embeddings.create(
        model=saved_data["model"],
        input=question,
    )
    question_embedding = response.data[0].embedding

    results = []

    for chunk in saved_data["chunks"]:
        score = cosine_similarity(
            question_embedding,
            chunk["embedding"],
        )

        results.append({
            "id": chunk["id"],
            "source": chunk["source"],
            "section": chunk["section"],
            "text": chunk["text"],
            "score": score,
        })

    results.sort(key=lambda result: result["score"], reverse=True)
    selected = results[:top_k]

    if not selected:
        return []

    # Include the rest of the highest-ranked document so related
    # policies, limitations, and exceptions remain available.
    primary_source = selected[0]["source"]
    selected_ids = {result["id"] for result in selected}

    for result in results:
        if (
            result["source"] == primary_source
            and result["id"] not in selected_ids
        ):
            selected.append(result)
            selected_ids.add(result["id"])

    return selected


if __name__ == "__main__":
    question = input("Ask a question: ").strip()
    results = search(question, top_k=10)

    for rank, result in enumerate(results, start=1):
        print(f"\n--- Result {rank} | Similarity: {result['score']:.3f} ---")
        print(f"Source: {result['source']}")
        print(f"Section: {result['section']}")
        print(result["text"])