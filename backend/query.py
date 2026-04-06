import os
from groq import Groq

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load embeddings
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load DB
db = Chroma(
    persist_directory="../database",
    embedding_function=embedding
)


def get_answer(query):
    try:
        docs = db.similarity_search(query, k=3)

        # If nothing found
        if not docs:
            return "I don't have information in the manual."

        context = " ".join([doc.page_content for doc in docs])

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are an EV diagnostic assistant.

Use ONLY the below context to answer.
If answer not found, say:
"I don't have information in the manual."

Context:
{context}

Question:
{query}

Answer clearly step-by-step.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"