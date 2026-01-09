# free-local-RAG-chatbot

In this repository are the scripts to make a Retrieval Augemented Generation (RAG) chatbot. This chatbot is completely free and locally hosted.
For the AI model: I used Ollama which allows the user to download pretrained LLM models to their local machine for free.
RAG chatbots require vector databases. I chose Weaviate, as it is an open-source, cloud native vector database.
I used docker desktop to host my instances of Weaviate.

# First Run
The first time this chatbot is created, the information needs to be gathered and vectorized. I gathered information via website crawling and scraping, so that is part of my process in this repository. There are other ways to gather the data that you want you're RAG chatbot to be able to call upon.

The basic steps for this **data preparation** are:
1. Website crawl and scrape (Website_crawl_scrape.py)
2. Scraped data cleaning (Clean_raw_text.py)
3. Chunking cleaned text to prepare for vectorization (Chunk_cleaned_text.py)

After the data has been gathered on your machine and prepared for vectorization, it is time to start with Weaviate.
Weaviate has excellent [documentation](https://docs.weaviate.io/weaviate).

The basic steps to vectorize the data with **Weaviate** are:
1. Boot up Weaviate with docker (docker-compose.yml)
2. Create the collections that your data will be stored in (create_knowledge_chunks_collection.py)
3. Import your data into Weaviate collections (import_knowledge_chunks_data.py)

The above steps are preparation. Once they have been completed all that is left is:
1. Query your RAG chatbot (RAG_example.py)
   

As a quick summary, this is the order the scripts should be run in when starting from scratch: 
Website_crawl_scrape, Clean_raw_text, Chunk_cleaned_text,
docker-compose.yml, create_knowledge_chunks_collection, import_knowledge_chunks_data
RAG_example


# If Data is Already Loaded
If you have already completed the data preparation steps and set up your Weaviate collections, then all you need to do is turn on your Weaviate instance via docker and run your RAG script.

If the pages have already been loaded and don't need to be updated, just run the following:
1. start docker desktop
2. docker-compose.yml
3. RAG_example.py
