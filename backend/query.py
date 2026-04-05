import os
from groq import Groq

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 📁 Path fix
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../database")

# 🔗 Embedding model
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 📦 Load DB
db = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embedding
)

def get_answer(query):
    try:
        query_lower = query.lower()

        # 🟢 Smart chat handling
        if query_lower in ["hi", "hello"]:
            return "Hello! Ask me about EV diagnostics."

        if query_lower in ["thank you", "thanks"]:
            return "You're welcome! Happy to help with EV diagnostics."

        if "your name" in query_lower:
            return "I am an EV Diagnostic Assistant designed to help with vehicle manuals."

        # 🔍 Retrieve docs
        docs = db.similarity_search(query, k=5)

        if not docs:
            return "I don't have information in the manual."

        # 📄 Build context with page numbers
        context = "\n\n".join([
            f"(Page {doc.metadata.get('page', 'N/A')})\n{doc.page_content}"
            for doc in docs
        ])

        # ❌ Weak context
        if len(context.strip()) < 50:
            return "I don't have information in the manual."

        # 🤖 LLM call
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        final_prompt = f"""
You are a strict EV diagnostic assistant.

IMPORTANT RULES:
1. Answer ONLY using the provided context.
2. DO NOT use your own knowledge.
3. DO NOT guess.
4. If the answer is not clearly in the context, reply EXACTLY:
"I don't have information in the manual."

Answer clearly in steps and include page reference if available.

Context:
{context}

Question:
{query}

Answer:
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": final_prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"