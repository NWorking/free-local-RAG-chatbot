# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# data for ingestion is from chunked_pages.json  If you have your own data file, change it to be the correct one
COPY chunked_pages.json . 

# Copy your code
COPY create_knowledge_chunks_collection.py .
COPY import_knowledge_chunks_data.py .
COPY multi_turn_RAG_conversation.py .
COPY app.py .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
