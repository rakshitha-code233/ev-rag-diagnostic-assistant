from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
def get_answer(query):
    return f"This is a demo answer for: {query}"

# Load embedding + DB
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

db = Chroma(
    persist_directory="vectorstore",
    embedding_function=embeddings
)

llm = OllamaLLM(model="phi")

def get_answer(query):
    try:
        # STEP 1: Search from PDF
        docs = db.similarity_search(query, k=2)

        if len(docs) > 0:
            context = " ".join([doc.page_content for doc in docs])

            prompt = f"""
You are an EV diagnostic assistant.

STRICT RULES:
- Answer ONLY using the given context
- If answer not in context → say "Not found in manual"
- Keep answer within 2-3 lines
- DO NOT create stories, puzzles, or extra content

Context:
{context}

Question: {query}

Answer:
"""

            response = llm.invoke(prompt)

            if response and "not found" not in response.lower():
                return response.strip()

        # STEP 2: General EV answer (fallback)
        fallback_prompt = f"""
You are an EV expert.

STRICT RULES:
- Answer only about electric vehicles
- Keep answer short (1-2 lines)
- No puzzles, no extra explanations

Question: {query}

Answer:
"""

        response = llm.invoke(fallback_prompt)
        return response.strip()

    except Exception as e:
        return f"Error: {str(e)}"