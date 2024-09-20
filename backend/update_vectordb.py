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
from groq import Groq

loader = DirectoryLoader('new_pdfs',glob='*.pdf')
docs = loader.load()

os.environ['PINECONE_API_KEY'] = ""
os.environ['OPENAI_API_KEY'] = ""
os.environ['GROQ_API_KEY'] = ""

# embeddings = HuggingFaceEmbeddings()
embeddings = OpenAIEmbeddings(model='text-embedding-3-large')
index_name = "lono"

vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

if(len(docs)!=0):
    vector_store.add_documents(docs)

# def process_pdf(file_path):
#     loader = PyPDFLoader(file_path)
#     pages = loader.load_and_split()
    
#     # Split the pages into smaller chunks
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
#     docs = text_splitter.split_documents(pages)
    
#     # Add to Pinecone
#     vector_store.add_documents(docs)
#     print(f"Added {len(docs)} chunks from {file_path} to Pinecone")

# def update_knowledge_base(pdf_dir):
#     for filename in os.listdir(pdf_dir):
#         if filename.endswith(".pdf"):
#             file_path = os.path.join(pdf_dir, filename)
#             process_pdf(file_path)

# if __name__ == "__main__":
#     pdf_directory = "/path/to/your/pdf/directory"
#     update_knowledge_base(pdf_directory)
#     print("Knowledge base update complete!")