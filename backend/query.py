from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

# Step 1: Load the vector database
embeddings = HuggingFaceEmbeddings()

#Load the vector database
db = Chroma(
    persist_directory="../vectorstore",
    embedding_function=embeddings
)

#load LLM(OpenAI)
llm = OllamaLLM(model = "phi")

#Ask a question
query = input("Ask your question: ")

#step 1 : Retrieve relevant docs
docs = db.similarity_search(query, k=1)

#step 2 : combine context
context = docs[0].page_content[:500]

#step 3 : crete prompt
prompt = f"""
You are an EV diagnostic assistant.

STRICT RULES:
- Answer ONLY the question
- Use ONLY the given context
- Do NOT add extra explanation
- Do NOT create stories or examples
- Stop after giving answer
- Maximum 3 lines

Context:
{context}

Question: {query}

Answer clearly:
"""

#step 4 : get AI answer
response = llm.invoke(prompt).strip()

#keep only first 3 lines
response = "\n".join(response.split("\n")[:3])  # Limit to 3 lines

print(f"\nAI Answer:\n")
print(response) 