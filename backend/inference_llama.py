from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from pinecone import Pinecone
import os
import glob
from groq import Groq

os.environ['PINECONE_API_KEY'] = "fa6ac8c5-59a4-4499-be3c-8fd306479607"
os.environ['GROQ_API_KEY'] = "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"
os.environ['OPENAI_API_KEY'] = "sk-x_ks7fHGew5kdHfFFR8mJWceEc3Ml8TmwjW87DamZoT3BlbkFJYvlFAjcRQrdbxSRqf4qllc-qJyYp1BO2KrN3L21msA"

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
index_name = "lono"

pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index(index_name)

def get_docs(query: str, top_k: int) -> list[str]:
    # encode query
    query_embedding = embeddings.embed_query(query)
    # search pinecone index
    res = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    # get doc text
    docs = [x["metadata"]['text'] for x in res["matches"]]
    return docs

def generate(query: str, docs: list[str]):
    system_message = (
        "You are a helpful assistant that answers questions about AI using the "
        "context provided below. If the context is empty or not helpful in answering the "
        "question then try to answer the question as best as possible with your own built in knowledge. "
        "If you can’t answer the question with your own built in knowledge just explain that you don’t have the context or enough info to answer the question. "
        "Don't say 'according to the context' or anything like that in your response.\n\n"
        "CONTEXT:\n"
        "\n---\n".join(docs)
    )
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": query}
    ]
    # generate response
    chat_response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return chat_response.choices[0].message.content

# query = "Tell me about Hope Haven Homeless Shelter"
query = "Which is the only orginization that provides funding?"

docs = get_docs(query, top_k=5)
out = generate(query=query, docs=docs)
print(out)


