
# Import data from previously gathered, cleaned, and chunked JSON file into the newly made collections

import weaviate
import json

client = weaviate.connect_to_local()
knowledge_chunks = client.collections.use("KnowledgeChunk")

with open("chunked_pages.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

with knowledge_chunks.batch.fixed_size(batch_size=100) as batch:
    for chunk in chunks:
        batch.add_object(
            {
                "url": chunk["url"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
            }
        )
        if batch.number_errors > 10:
            print("Batch import stopped due to excessive errors.")
            break

if knowledge_chunks.batch.failed_objects:
    print(f"Failed imports: {len(knowledge_chunks.batch.failed_objects)}")

client.close()
