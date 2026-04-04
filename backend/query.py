import os
from groq import Groq

# Updated imports (no deprecation)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 📁 Fix path (VERY IMPORTANT)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔗 Load embedding model
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 📦 Load vector database
db = Chroma(
    persist_directory=os.path.join(BASE_DIR, "../database"),
    embedding_function=embedding
)

def get_answer(query):
    try:
        # 🔍 STEP 1: Search in vector DB
        docs = db.similarity_search(query, k=3)

        # ❌ If nothing found
        if not docs:
            return "I don't have information in the manual."

        # 📄 Build context
        context = " ".join([doc.page_content for doc in docs])

        # ❌ Weak context protection
        if len(context.strip()) < 50:
            return "I don't have information in the manual."

        # 🤖 STEP 2: Call LLM
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        final_prompt = f"""
You are a strict EV diagnostic assistant.

IMPORTANT RULES:
1. Answer ONLY using the provided context.
2. DO NOT use your own knowledge.
3. DO NOT guess.
4. If the answer is not clearly in the context, reply EXACTLY:
"I don't have information in the manual."

Context:
{context}

Question:
{query}

Answer:
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": final_prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"