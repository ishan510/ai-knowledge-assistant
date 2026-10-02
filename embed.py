import json

from dotenv import load_dotenv
from openai import OpenAI

from ingest import PROJECT_DIR

MODEL = "text-embedding-3-small"
CHUNKS_PATH = PROJECT_DIR / "data" / "chunks.json"
OUTPUT_PATH = PROJECT_DIR / "data" / "embeddings.json"


def main():
    load_dotenv(PROJECT_DIR / ".env")
    client = OpenAI()

    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError("No chunks found. Run chunk.py first.")

    if OUTPUT_PATH.exists():
        raise FileExistsError(
            "embeddings.json already exists. To intentionally rebuild "
            "the embeddings, delete that file and run this script again."
        )

    print(f"Generating embeddings for {len(chunks)} chunks...")

    response = client.embeddings.create(
        model=MODEL,
        input=[chunk["text"] for chunk in chunks],
    )

    # Match each returned embedding to its original input position.
    vectors = {
        item.index: item.embedding
        for item in response.data
    }

    if set(vectors) != set(range(len(chunks))):
        raise ValueError("The API did not return an embedding for every chunk.")

    records = [
        {**chunk, "embedding": vectors[index]}
        for index, chunk in enumerate(chunks)
    ]

    result = {
        "model": MODEL,
        "dimensions": len(vectors[0]),
        "chunks": records,
    }

    OUTPUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(records)} embeddings.")
    print(f"Dimensions per embedding: {result['dimensions']}")
    print(f"Tokens used: {response.usage.total_tokens}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()