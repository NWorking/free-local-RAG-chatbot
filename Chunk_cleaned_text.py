
# Chunking breaks down text into chunks that the embedding model can vectorize - Necessary for RAG

# Takes pages_clean.json as input
# Splits text into chunks of ~800 characters by default. 
# The strategy used here makes sure chunks are made up of whole sentences. 
# It also carries over some information from the previous chunk to preserve all information, improving RAG performance
# Returns chunked_pages.json

import re
import json
from pathlib import Path

def sentence_split(text):
    """Split text into sentences using regex."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text, max_chars=800, overlap=150):
    """Split text into overlapping chunks, sentence-aware."""
    sentences = sentence_split(text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        # If adding this sentence would exceed max length, finalize the current chunk
        if sum(len(s) for s in current_chunk) + len(sentence) > max_chars:
            chunk = " ".join(current_chunk).strip()
            if chunk:
                chunks.append(chunk)

            # Start a new chunk, beginning with overlap from previous chunk
            overlap_text = chunk[-overlap:]
            current_chunk = [overlap_text, sentence]
        else:
            current_chunk.append(sentence)

    # Add any leftover text
    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks


# ===  usage with cleaned JSON ===
input_path = Path("pages_clean.json")   # input JSON file from cleaning step
output_path = Path("chunked_pages.json")

with input_path.open("r", encoding="utf-8") as f:
    pages = json.load(f)

chunked_data = []
for page in pages:
    url = page["url"]
    text = page["text"]
    chunks = chunk_text(text, max_chars=800, overlap=150)
    for i, chunk in enumerate(chunks):
        chunked_data.append({
            "url": url,
            "chunk_id": f"{url}#chunk{i}",
            "text": chunk
        })

with output_path.open("w", encoding="utf-8") as f:
    json.dump(chunked_data, f, indent=2, ensure_ascii=False)

print(f"Chunking complete. {len(chunked_data)} chunks written to {output_path}")
