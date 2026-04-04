import os
from groq import Groq

# RAG imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load embeddings
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector DB (IMPORTANT PATH)
db = Chroma(
    persist_directory="../database/chroma",
    embedding_function=embedding
)

def get_answer(query):
    try:
        # 🔍 STEP 1: Search in PDF
        docs = db.similarity_search(query, k=3)

        # If nothing found
        if not docs:
            return "I don't have information in the manual."

        # Create context
        context = " ".join([doc.page_content for doc in docs])

        # If context empty
        if context.strip() == "":
            return "I don't have information in the manual."

        # 🤖 STEP 2: AI call
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        final_prompt = f"""
You are an EV diagnostic assistant.

Use ONLY the below context to answer.
Do NOT use your own knowledge.
If answer is not in context, say:
"I don't have information in the manual."

Context:
{context}

Question:
{query}

Answer clearly and step-by-step.
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