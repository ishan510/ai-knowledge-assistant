from pathlib import Path

# Locate the documents relative to this script.
PROJECT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge_base"


def load_documents():
    if not KNOWLEDGE_DIR.is_dir():
        raise FileNotFoundError(
            f"Knowledge base folder not found: {KNOWLEDGE_DIR}"
        )

    documents = []

    for file_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            raise ValueError(f"Document is empty: {file_path.name}")

        documents.append({
            "source": file_path.name,
            "text": content,
        })

    if not documents:
        raise ValueError("No Markdown documents found in knowledge_base.")

    return documents


if __name__ == "__main__":
    documents = load_documents()

    for document in documents:
        word_count = len(document["text"].split())
        print(f"{document['source']}: {word_count} words")

    print(f"\nLoaded {len(documents)} documents successfully.")