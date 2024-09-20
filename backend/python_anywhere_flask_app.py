from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
import pytz
from langchain_community.embeddings import OpenAIEmbeddings
from pinecone import Pinecone
from groq import Groq

# Set the proxy URL
proxy_url = "http://proxy.server:3128"

# Set environment variables for the proxy
os.environ['HTTP_PROXY'] = proxy_url
os.environ['HTTPS_PROXY'] = proxy_url


# Set up API keys (ensure these are set securely)
os.environ['PINECONE_API_KEY'] = "fa6ac8c5-59a4-4499-be3c-8fd306479607"
os.environ['GROQ_API_KEY'] = "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"
os.environ['OPENAI_API_KEY'] = "sk-x_ks7fHGew5kdHfFFR8mJWceEc3Ml8TmwjW87DamZoT3BlbkFJYvlFAjcRQrdbxSRqf4qllc-qJyYp1BO2KrN3L21msA"

# Initialize clients
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
index_name = "lono"

# Initialize Pinecone client with proxy configuration
pc = Pinecone(
    api_key=os.environ['PINECONE_API_KEY'],
    proxy_url=proxy_url
)
index = pc.Index(index_name)

# Initialize Flask app
app = Flask(__name__)
CORS(
    app,
    resources={
        r"/chat": {"origins": "*"},
    },
)

def log_api_usage(endpoint_name, prompt, completion, total):
    # Get the absolute path to the directory this file is in
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Create a directory for the logs if it doesn't exist
    logs_dir = os.path.join(dir_path, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Open the log file for the endpoint
    log_file = os.path.join(logs_dir, f"{endpoint_name}.txt")
    with open(log_file, "a") as f:
        # Get current time in UTC
        now_utc = datetime.datetime.now(pytz.timezone("UTC"))
        # Convert to HST
        now_hst = now_utc.astimezone(pytz.timezone("Pacific/Honolulu"))
        # Format the datetime
        formatted_time = now_hst.strftime("%m/%d/%Y %I:%M %p")
        # Write the current time and the number of tokens used to the log file
        f.write(
            f"{formatted_time}. Prompt: {prompt}. Completion: {completion}. Total: {total}.\n"
        )

def get_docs(query: str, top_k: int) -> list:
    # Encode query
    query_embedding = embeddings.embed_query(query)
    # Search Pinecone index
    res = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    # Get document text
    docs = [x["metadata"]['text'] for x in res["matches"]]
    return docs

def generate(query: str, docs: list, message_history: list):
    system_message = (
        "You are a helpful assistant named Lono that answers questions from the user using the context and message history. "
        "Each orginization in the context is different and don't assume that they are connected in any way. "
        "Read the descriptions to reason about the different orginizations and answer the user's query as best as possible. If the context is empty or not helpful in answering the "
        "question then try to answer the question as best as possible with your own built-in knowledge. "
        "If you can’t answer the question with your own built-in knowledge, just explain that you don’t have the context or enough info to answer the question. "
        "Don't say 'according to the context' or anything like that in your response. Don't respond in markdown, use normal text.\n\n"
        "CONTEXT:\n"
        "\n---\n".join(docs)
    )
    messages = [
        {"role": "system", "content": system_message}
    ] + message_history[:-1] + [
        {"role": "user", "content": query}
    ]
    # Generate response
    chat_response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return chat_response

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    message_history = data.get("history", [])

    top_k = 5

    docs = get_docs(query, top_k)
    response = generate(query=query, docs=docs, message_history=message_history)

    # Extract the response text
    response_text = response.choices[0].message.content

    # Log API usage
    # Estimate token counts if actual counts are not available
    prompt_length = len(query) + sum(len(doc) for doc in docs)
    completion_length = len(response_text)
    total_length = prompt_length + completion_length

    log_api_usage("chat", prompt_length, completion_length, total_length)

    return jsonify({"result": response_text})

if __name__ == "__main__":
    app.run(debug=True)
