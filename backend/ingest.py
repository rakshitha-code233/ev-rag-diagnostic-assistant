from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

# Step 1: Load PDF documents
folder_path = "../data/manuals"
all_docs = []

for file in os.listdir(folder_path):
    if file.endswith(".pdf"):
        path = os.path.join(folder_path, file)
        loader = PyPDFLoader(path)
        docs = loader.load()
        all_docs.extend(docs)

print("Loaded pages:", len(all_docs))

# Step 2: Split documents into smaller chunks
text_splitter = CharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=50
)

texts = text_splitter.split_documents(all_docs)
print("Split into chunks:", len(texts))

# Step 3: Create embeddings
embeddings = HuggingFaceEmbeddings()

# Step 4: Store in Chroma vector database
vector_db = Chroma.from_documents(
    texts, 
    embeddings, 
    persist_directory="../vectorstore"
)

print("Embeddings stored successfully!")