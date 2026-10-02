from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Northstar password reset links expire after 30 minutes.",
)

embedding = response.data[0].embedding

print("OpenAI connection successful.")
print(f"Embedding dimensions: {len(embedding)}")
print(f"Tokens used: {response.usage.total_tokens}")