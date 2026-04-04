import os
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Correct path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory=os.path.join(BASE_DIR, "../database"),
    embedding_function=embedding
)

def get_answer(query):
    try:
        # 🔍 Search
        docs = db.similarity_search(query, k=3)

        if not docs:
            return "I don't have information in the manual."

        context = " ".join([doc.page_content for doc in docs])

        # 🤖 AI
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        final_prompt = f"""
You are an EV diagnostic assistant.

Use ONLY the below context to answer.
If not found, say: I don't have information in the manual.

Context:
{context}

Question:
{query}

Answer clearly step-by-step.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": final_prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"