
# Creates the empty "collections" which are the containers that will hold the data that was chunked in a previous step
# Also configures the LLM and embedding model to use for vectorization
# By including url as a collections property, the chatbot will be able to include links to where it got its information in its responses

import weaviate
from weaviate.classes.config import Property, DataType, Configure

# Uncomment this line if you are needing to REIMPORT data:
# client.collections.delete("KnowledgeChunk")

# Can use connect to local for local development/testing
# client = weaviate.connect_to_local()

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

client = weaviate.connect_to_custom(
    http_host=os.getenv("WEAVIATE_HOST", "weaviate"),
    http_port=int(os.getenv("WEAVIATE_HTTP_PORT", 8080)),
    http_secure=False,
    grpc_host=os.getenv("WEAVIATE_HOST", "weaviate"),
    grpc_port=int(os.getenv("WEAVIATE_GRPC_PORT", 50051)),
    grpc_secure=False
)

# If the collection already exists, no need to remake it
if client.collections.exists("KnowledgeChunk"):
    print("Collection already exists, skipping creation.")
else:
    # Create a new collection for your RAG documents
    knowledge_chunks = client.collections.create(
        name="KnowledgeChunk",
        properties=[
            Property(name="url", data_type=DataType.TEXT),
            Property(name="chunk_id", data_type=DataType.TEXT),
            Property(name="text", data_type=DataType.TEXT),
        ],
        vector_config=Configure.Vectors.text2vec_ollama(
            api_endpoint=OLLAMA_URL, # "http://host.docker.internal:11434" <-- for local development using docker, "http://localhost:11434" if not using docker
            model="nomic-embed-text",
        ),
        generative_config=Configure.Generative.ollama(
            api_endpoint=OLLAMA_URL, # "http://host.docker.internal:11434" <-- for local development using docker, "http://localhost:11434" if not using docker
            model="llama3.2"
        )
    )
    
    client.close()
