# free-local-RAG-chatbot

In this repository are the scripts to make a Retrieval Augemented Generation (RAG) chatbot. This chatbot is completely free and locally hosted.

For the AI model: I used <ins>Ollama</ins> which allows the user to download pretrained LLM models to their local machine for free. Specifically, I am using the Llama 3.2 model from Meta.

RAG chatbots require vector databases. I chose <ins>Weaviate</ins>, as it is an open-source, cloud native vector database.

I used docker desktop to host my instances of Weaviate.

**Prerequisites** - Both of these are free to install

- Docker desktop installed
- Ollama installed

**Important** - 

I gathered the data that my RAG chatbot would base its responses off of from a website. I did not have access to the backend of this website, so I had to scrape it. 
The idea was that it would be deployed on this website after being proved to be successful. <ins> You do not need to scrape a website if you already have the file or files containing the information your RAG chatbot should base its responses off of. </ins> It would still be a good idea to clean your information file(s). It will still be necessary to chunk that information.

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
docker-compose.yml, create_knowledge_chunks_collection, import_knowledge_chunks_data,
RAG_example


# If Data is Already Loaded
If you have already completed the data preparation steps and set up your Weaviate collections, then all you need to do is turn on your Weaviate instance via docker and run your RAG script.

If the pages have already been loaded and don't need to be updated, just run the following:
1. start docker desktop
2. docker-compose.yml
3. RAG_example.py


# Once This is Successful
Congratualtions! You got the basics down. The next steps are creating a frontend and making your RAG chatbot smarter. 

The new workflow, assuming your data is loaded in is:
1. Start docker desktop
2. Change your directory in your terminal to point towards where ever these scripts are located
3. In your terminal run: docker compose up -d
4. In your terminal run: streamlit run app.py

# Frontend
I have a basic Streamlit powered frontend to allow a user to query the chatbot. This is in the file **app.py**. 

# Enhancing the chatbot
1. <ins>Prompt Modes</ins>
In the multi_turn_RAG_conversation.py file, there is a much more in depth RAG set up. This file has **prompt modes** which allow the chatbot to have different prompt instructions for answering different types of questions. The prompts provided are for Extraction, Information, and Guidance modes. An unlimited number of modes can be added to have your chatbot have the best possible operating instructions related to what it is queried with. The specific prompt mode is decided in the core RAG logic (in the chat function) via a keyword router. This is an inexpensive way to try to see what the user needs and pick the prompt mode that is best for that function.

2. <ins>Query Rewriting</ins>
The logic below the prompt modes is for query rewriting and when queries should be rewritten. This enables the chatbot to have context and memory of recent exchanges in the current conversation. The conversation history is saved to a dictionary in the core RAG logic (in the chat function). The **rewrite_query** function takes in the current query and access the past 3 turns of conversation. It then calls Ollama to rewrite the query with conversation history as context. This rewritten query is then used in place of the users original query, so the chatbot has some context. The **needs_rewriting** funtion checks for keywords in the users query to see if rewriting is necessary. This check is because any call to an LLM is taxing. In the event of query rewriting, latency and compute are increased. Users do not like this. This function tries to avoid rewriting where possible, to save resources.

An example of where query rewriting would be useful is a conversation where the user asks "What is the largest national park?" then follows up in their next query with "Where is it located?". Without conversation history, the chatbot would not know what "it" is referencing in the users second query.

3. <ins>Logging</ins>
The core RAG logic is also enhanced in this file with basic logging. It is currently set up to capture some useful information, such as: time, user, query, prompt mode, and LLM parameters. These logs are saved to the local machine, so they can be read anytime, even if docker is not running.

# Areas for Improvement
<ins>Term Mapping</ins>
Chatbots can struggle with abbreviations. For instance, if you were making this chatbot for the Department of Artificial Intelligence Development, it is very likely that users would not want to type that every time, and would like to just type the abreviation: DAID. If you know there are likely to be instances like this for your where you plan to implement your chatbot. It would be good to give it a dictionary of common terms you might expect useres to use. This can be passed directly into the prompt so the chatbot can reference it when necessary.
