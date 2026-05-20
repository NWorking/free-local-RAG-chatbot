# This expands on RAG_example.py with prompt modes, prompt engineering, and
# multi-turn conversation with memory and logging

import json
import requests

import weaviate
from weaviate.classes.generate import GenerativeConfig
from weaviate.classes.init import AdditionalConfig, Timeout

# environment variables
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

#----PROMPT MODES-------------------------------------------------------------------------------------------------------
# Different prompts are better for different tasks
# A keyword router will decide what prompt mode best fits the user query


def get_extract_prompt(q):
    return f"""You are a direct information extraction system. DO NOT write code. DO NOT explain.
    Any mention of the [abreviation] refers to the [expanded abreviation]
    
    Question: {q}

    If this chunk does not contain the answer, respond with ONLY:
    This information is not in my data
    
    If this chunk contains the answer, extract the answer and respond with the extracted answer
    AND respond with the url in EXACTLY this format:
  
    Source: {{url}}

    DO NOT write Python code.
    DO NOT write explanations.
    DO NOT write functions.

    Chunk: {{text}}"""


def get_guidance_prompt(q):
    return f"""Based on the provided context, suggest the most relevant resource.
        Any mention of the [abreviation] refers to the [expanded abreviation]

        question = {q}
        
        Only use information from the context.
        Do not invent roles or services.
        
        your response should ALWAYS include one {{url}} related to the context
        
        If no guidance can be determined, respond with:
        "The requested information is not available in the provided documents."
        """


def get_information_prompt(q):
    return f"""Answer the user's question using the provided context.
        Any mention of the [abreviation] refers to the [expanded abreviation]

        question = {q}

        Synthesize the information when needed, but do not add facts that are not present in the context.
        
        your response should ALWAYS include one {{url}} related to the context 

        Be concise and helpful.
        """




#---QUERY REWRITING FOR MEMORY------------------------------------------------------------------------------------------

def rewrite_query(current_query, conversation_history):
    """
    Rewrite query to be standalone using conversation context

    Args:
        current_query: The user's current question
        conversation_history: List of dicts with 'user' and 'assistant' keys

    Returns:
        Rewritten standalone query
    """

    # Format conversation history
    history_text = ""
    for turn in conversation_history[-3:]:  # Last 3 turns to keep it focused
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"

    prompt = f"""Previous conversation:
        {history_text}
        
        Current question: {current_query}
        
        Task: Rewrite the current question to be standalone by replacing pronouns (their, his, her, it, etc.) with the
        specific NOUN being referenced from the conversation history.
        
        Any mention of the [abreviation] refers to the [expanded abreviation]
        
        Rules:
        - Output ONLY the rewritten question
        - Do NOT answer the question
        - Do NOT add explanations
        - Keep the same question format
        
        Rewritten question:"""

    # Call Ollama - Just Ollama because it doesn't need context from the database to rewrite the query
    response = requests.post(
        OLLAMA_URL, # "http://localhost:11434/api/generate",  <-- use this for local development
        json={
            "model": "llama3.2",  # or whatever model is being used
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1  # Low temp for consistent rewrites
        }
    )

    result = response.json()
    rewritten = result['response'].strip()

    # Clean up common issues
    if rewritten.startswith('"') and rewritten.endswith('"'):
        rewritten = rewritten[1:-1]

    return rewritten


# Rewriting involves an extra LLM call, so if it is not necessary, it should try to be avoided
def needs_rewriting(query):
    """
    Check if query contains pronouns or is a follow-up question
    """
    pronouns = ["their", "his", "her", "its", "them", "they", "he", "she", "it"]
    follow_up_words = ["also", "too", "as well", "what about"]

    query_lower = query.lower()

    # Check for pronouns
    if any(pronoun in query_lower for pronoun in pronouns):
        return True

    # Check for follow-up indicators
    if any(word in query_lower for word in follow_up_words):
        return True

    return False



#---RETRIEVAL AUGEMENTED GENERATION-------------------------------------------------------------------------------------



# connect_to_local for local development, connect_to_custom for using docker
# client = weaviate.connect_to_local(
#     # port=8080,
#     # grpc_port=50051,
#     additional_config=AdditionalConfig(
#         timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
#     )
# )

client = weaviate.connect_to_custom(
    http_host=os.getenv("WEAVIATE_HOST", "weaviate"),
    http_port=int(os.getenv("WEAVIATE_HTTP_PORT", 8080)),
    http_secure=False,
    grpc_host=os.getenv("WEAVIATE_HOST", "weaviate"),
    grpc_port=int(os.getenv("WEAVIATE_GRPC_PORT", 50051)),
    grpc_secure=False,
    additional_config=AdditionalConfig(
        timeout=Timeout(init=60, query=120, insert=120))
)

# Initialize conversation storage
conversation_history = []
def chat(user_query):
    """
    Main chat function with memory

    Args:
        user_query: The user's current question
        prompt_modes: List of string prompts that determine the mode of the bot

    Returns:
        answer: the chatbots response
    """

    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('logs/chatbot.log', maxBytes=10*1024*1024, backupCount=5),
            #logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    analytics_logger = logging.getLogger('analytics')
    analytics_handler = RotatingFileHandler('logs/analytics.log', maxBytes=10*1024*1024, backupCount=5)
    analytics_handler.setFormatter(logging.Formatter('%(message)s'))
    analytics_logger.addHandler(analytics_handler)
    analytics_logger.setLevel(logging.INFO)

    start_time = datetime.now()
    answer = None

    logger.info(f"[Session: {session_id}] New query: '{user_query}'")
    
    # Step 1: Check if we need to rewrite
    if conversation_history and needs_rewriting(user_query):
        logger.info("Query needs rewriting (contains pronouns/follow-up words)")
        print(f"Original query: {user_query}")
        user_query = rewrite_query(user_query, conversation_history)
        print(f"Rewritten query: {user_query}")

    # Keyword Router
    q = user_query
    q= q.lower()
    prompt_mode = ""
    if any(k in q for k in ["email", "phone", "address", "hours", "locat", "contact", "office"]):
        mode = get_extract_prompt(q) # extract
        prompt_mode = "extract"
        temp = 0.01
        a = 0.05
        print("MODE = EXTRACT")
        logger.info(f"Mode: EXTRACT (alpha={a}, temp={temp})")
    elif any(k in q for k in ["who should", "who do i", "how do i"]):
        mode = get_guidance_prompt(q) # guidance
        prompt_mode = "guidance"
        temp = 0.2
        a = 0.25
        print("MODE = GUIDANCE")
        logger.info(f"Mode: GUIDANCE (alpha={a}, temp={temp})")
    else:
        mode = get_information_prompt(q) # information
        prompt_mode = "information"
        temp = 0.2
        a = 0.25
        print("MODE = INFORMATION")
        logger.info(f"Mode: INFORMATION (alpha={a}, temp={temp})")


    # EXTRACT MODE
    # needs specific information, therefore single_prompt is used instead of grouped_task so that information can be
    # extracted exactly from a specific chunk and the correct URL associated with that specific chunk can be returned
    if prompt_mode == "extract":

        knowledge = client.collections.use("KnowledgeChunk")
        print(knowledge.config.get())

        response = knowledge.generate.hybrid(
            query=q,
            limit=3,
            alpha=a,
            single_prompt=mode,
            generative_provider=GenerativeConfig.ollama(  # Configure the Ollama generative integration
                api_endpoint=OLLAMA_URL,  #"http://host.docker.internal:11434" <-- for local development using Docker,  # If NOT using Docker you might need: http://ollama:11434
                model="llama3.2",  # The model to use
                temperature=temp,
            ),
        )

        valid_response = False
        # Find the first chunk that has a real answer
        for obj in response.objects:
            # print(json.dumps(obj.properties, indent=2))
            # print(obj.generated)
            if "not in my data" not in obj.generated:
                answer = obj.generated # If the bot determines there is an appropriate response, this is it
                valid_response=True
                logger.info(f"Answer found in chunk: {obj.properties.get('url', 'unknown')}")
                break
        if valid_response == False:
            answer = response.objects[0].generated # If no appropriate answer is found, this returns a "not found" response
            logger.info("No valid answer found in any chunk")


    # other prompt modes can use grouped_task to produce a response based on aggregated retrieval
    else:
        knowledge = client.collections.use("KnowledgeChunk")
        print(knowledge.config.get())

        response = knowledge.generate.hybrid(
            query=q,
            limit=8,
            alpha=a,
            grouped_task=mode,
            generative_provider=GenerativeConfig.ollama(  # Configure the Ollama generative integration
                api_endpoint=OLLAMA_URL,  # "http://host.docker.internal:11434" <-- for local development using Docker,  # If NOT using Docker you might need: http://ollama:11434
                model="llama3.2",  # The model to use
                temperature=temp
            ),
        )
        answer = response.generative.text


    # Step 4: Store responses in conversation history
    conversation_history.append({
        "user": user_query,
        "assistant": answer
    })

    # Keep only last 5 turns to avoid context getting too long
    if len(conversation_history) > 5:
        conversation_history.pop(0)

    # Step 5: Log analytics
    duration = (datetime.now() - start_time).total_seconds()
    analytics_data = {
        "timestamp": start_time.isoformat(),
        "session_id": session_id,
        "user_query": user_query,
        "rewritten_query": q if q != user_query else None,
        "mode": prompt_mode,
        "response_time_seconds": round(duration, 2),
        # "success": not error_occurred,
        "answer_length": len(answer) if answer else 0
    }
    analytics_logger.info(json.dumps(analytics_data))

    logger.info(f"Response generated in {duration:.2f}s")

    return answer





if __name__ == "__main__":
    # Test unlimited convo
    test = ""
    while test != "end":
        print("=" * 50)
        test = input()
        # print("Test 1: Email question")
        print(chat(test))

    client.close()  # Free up resources



#---useful code & debug-------------------------------------------------------------------------------------------------

# Return the most common URL, not determined by LLM:
    # from collections import Counter
    #
    # urls = [obj.properties['url'] for obj in response.objects]
    # most_common_url = Counter(urls).most_common(1)[0][0]
    #
    # print(f"Primary source: {most_common_url}")

# look at the raw chunks returned
    # for obj in response.objects:
    #     print(json.dumps(obj.properties, indent=2))



