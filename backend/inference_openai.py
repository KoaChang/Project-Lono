from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from pinecone import Pinecone
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import os
import glob

os.environ['PINECONE_API_KEY'] = ""
os.environ['OPENAI_API_KEY'] = ""

embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
index_name = "lono"

# query = "What is 5+5?"
query = "Tell me about Hope Haven Homeless Shelter"

# Gpt-4o easier implementation with built in RetrievalQA from langchain
llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

qa = RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=vector_store.as_retriever())
response = qa.invoke(query)

print(response)

# similar_docs = vector_store.similarity_search(query)
# print(similar_docs)
