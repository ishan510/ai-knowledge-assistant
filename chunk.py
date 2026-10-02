import json

from ingest import PROJECT_DIR, load_documents


def chunk_document(document):
    chunks = []
    introduction = []
    section_title = None
    section_lines = []

    def save_section():
        body = "\n".join(section_lines).strip()

        if not body:
            return

        # Include the document title and metadata for context.
        context = "\n".join(introduction).strip()

        chunks.append({
            "id": f"{document['source']}::section-{len(chunks) + 1}",
            "source": document["source"],
            "section": section_title or "Introduction",
            "text": f"{context}\n\n## {section_title}\n{body}"
                    if section_title else body,
        })

    for line in document["text"].splitlines():
        if line.startswith("## "):
            save_section()
            section_title = line[3:].strip()
            section_lines = []
        elif section_title is None:
            introduction.append(line)
        else:
            section_lines.append(line)

    save_section()

    # Preserve documents that have no section headings.
    if not chunks:
        chunks.append({
            "id": f"{document['source']}::section-1",
            "source": document["source"],
            "section": "Full document",
            "text": document["text"],
        })

    return chunks


if __name__ == "__main__":
    documents = load_documents()
    chunks = []

    for document in documents:
        document_chunks = chunk_document(document)
        chunks.extend(document_chunks)
        print(f"{document['source']}: {len(document_chunks)} chunks")

    output_dir = PROJECT_DIR / "data"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "chunks.json"
    output_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nCreated {len(chunks)} chunks from {len(documents)} documents.")
    print(f"Saved to: {output_path}")

    print("\nExample chunk:")
    print(json.dumps(chunks[0], indent=2, ensure_ascii=False))