from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load documents
with open("documents.txt", "r", encoding="utf-8") as f:
    docs = f.readlines()

# Convert to embeddings
embeddings = model.encode(docs)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

# Save index
faiss.write_index(index, "faiss_index.index")

print("✅ FAISS index created successfully!")