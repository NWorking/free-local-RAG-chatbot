
# Creates the empty "collections" which are the containers that will hold the data that was chunked in a previous step
# Also configures the LLM and embedding model to use for vectorization

import weaviate
from weaviate.classes.config import Property, DataType, Configure

client = weaviate.connect_to_local()

# Create a new collection for your RAG documents
knowledge_chunks = client.collections.create(
    name="KnowledgeChunk",
    properties=[
        Property(name="url", data_type=DataType.TEXT),
        Property(name="chunk_id", data_type=DataType.TEXT),
        Property(name="text", data_type=DataType.TEXT),
    ],
    vector_config=Configure.Vectors.text2vec_ollama(
        api_endpoint="http://host.docker.internal:11434",  #"http://host.docker.internal:11434" if using Docker, or "http://localhost:11434 if not using docker"
        model="nomic-embed-text",
    ),
)

client.close()
