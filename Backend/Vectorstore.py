import getpass
import os
import tempfile
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_milvus import Milvus
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredEmailLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
    

def load_and_split_documents(file_paths: List[str]) -> List[Document]:
    """Load and split documents into chunks"""
    if not file_paths:
        raise ValueError("No file paths provided"):
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

gemini_api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
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
db_file = tempfile.NamedTemporaryFile(prefix="milvus_", suffix=".db", delete=False).name
print(f"The vector database will be saved to {db_file}")

# Initialize Milvus Vector Store
vector_db = Milvus(
    embedding_function=embeddings,
    collection_name="hybrid_collection",
    connection_args={
        "url": db_file,  # Your Milvus URI
        "token": user_token  # If authentication is required
    },
    vector_field="dense_vector",
    text_field="text",
    sparse_embedding_function=sparse_encoder,
    sparse_vector_field="sparse_vector",
    enable_hybrid_search=True
    auto_id=True,
    index_params={"index_type": "AUTOINDEX", "metric_type": "COSINE"},
    drop_old=False
)

def setup_vectorstore():
    """Initialize and populate the vector store"""
    # Load and split documents
    file_paths = ["insurance_policy_v3.pdf", "exclusions_clause.docx"]
    docs = load_and_split_documents(file_paths)
    
    print(f"Loaded {len(docs)} document chunks")
    
    # Add documents to Milvus
    vector_db.add_documents(docs)
    print("Documents indexed successfully!")
    
    return vector_db


