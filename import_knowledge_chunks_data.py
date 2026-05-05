
# Import data from previously gathered, cleaned, and chunked JSON file into the newly made collections

import weaviate
import json


#client = weaviate.connect_to_local()

client = weaviate.connect_to_custom(
    http_host=os.getenv("WEAVIATE_HOST", "weaviate"),
    http_port=int(os.getenv("WEAVIATE_HTTP_PORT", 8080)),
    http_secure=False,
    grpc_host=os.getenv("WEAVIATE_HOST", "weaviate"),
    grpc_port=int(os.getenv("WEAVIATE_GRPC_PORT", 50051)),
    grpc_secure=False
)

knowledge_chunks = client.collections.use("KnowledgeChunk")

# check if data is already ingested or not
# count records. If 0, no data is in, proceed with ingestion
if knowledge_chunks.aggregate.over_all(total_count=True).total_count > 0:
    print("Data already exists, skipping ingestion.")
    client.close()
else:
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
