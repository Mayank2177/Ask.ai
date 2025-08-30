import getpass
import os
from dotenv import load_dotenv
import tempfile
from typing import List
from langchain.schema import Document
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_milvus import Milvus
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
    

def load_and_split_documents(file_paths: List[str]) -> List[Document]:
    """Load and split documents into chunks"""
    if not file_paths:
        raise ValueError("No file paths provided")
    documents = []
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        elif path.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif path.endswith(".docx"):
            loader = Docx2txtLoader(path)
        elif path.endswith(".eml"):
            loader = UnstructuredEmailLoader(path)
        else:
            continue
        docs = loader.lazy_load()
        documents.extend(docs)

    # Split into chunks for indexing
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len,)
    return text_splitter.split_documents(documents)

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables!")
else:
    print("API key loaded successfully")

genai.configure(api_key=gemini_api_key)


# Initialize Gemini Embedding Model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="retrieval_document"  # Optimized for document retrieval
)

# Create temporary database file
db_file= os.getenv("MILVUS_URI")
user_token= os.getenv("MILVUS_TOKEN")


# Initialize Milvus Vector Store
vector_db = Milvus(
    embedding_function=embeddings,
    collection_name="hybrid_collection",
    connection_args={
        "uri": db_file,  # Your Milvus URI
        "token": user_token  # If authentication is required
    },
    vector_field="dense_vector",
    text_field="text",
    sparse_embedding_function=sparse_encoder,
    sparse_vector_field="sparse_vector",
    enable_hybrid_search=True,
    auto_id=True,
    index_params={"index_type": "AUTOINDEX", "metric_type": "COSINE"},
    drop_old=False
)

def setup_vectorstore(uploaded_file_paths: List[str] = None):
    """Initialize and populate the vector store"""
    
    # Use uploaded file paths if provided, otherwise fall back to default
    if uploaded_file_paths:
        file_paths = uploaded_file_paths
    else:
        print("File is not fethed successfully, try again")
    
    # Load and split documents
    docs = load_and_split_documents(file_paths)
    
    # Add documents to Milvus
    vector_db.add_documents(docs)
    print("Documents indexed successfully!")
    return vector_db





