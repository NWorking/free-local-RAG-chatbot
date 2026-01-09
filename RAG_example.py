
# A query is vectorized, then nearest neighbor search is done on the KnowledgeChunk collections
# A response is formulated based on the instructions in grouped_task, then printed
# You now have a local RAG chatbot!

import weaviate
from weaviate.classes.generate import GenerativeConfig

client = weaviate.connect_to_local()

knowledge = client.collections.use("KnowledgeChunk")

response = knowledge.generate.near_text(
    query="What is the company",
    limit=2,
    grouped_task="Give a succinct answer with a url link to a relevant page.",
    generative_provider=GenerativeConfig.ollama(  # Configure the Ollama generative integration
        api_endpoint="http://host.docker.internal:11434",  # If NOT using Docker you might need: http://ollama:11434
        model="llama3.2",  # The model to use
    ),
)

print(response.generative.text)  # Inspect the generated text

client.close()  # Free up resources
