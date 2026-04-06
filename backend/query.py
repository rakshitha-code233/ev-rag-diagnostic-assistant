import os
from groq import Groq

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings
from db import search_knowledge

# ✅ SAFE embedding (no crash)
embedding = FakeEmbeddings(size=384)

db = Chroma(
    persist_directory="../database",
    embedding_function=embedding
)


def get_answer(query):
    query_lower = query.lower()

    # -------- GREETINGS --------
    if query_lower in ["hi", "hello", "hey"]:
        return "Hello 👋 How can I help you?"

    if "thank" in query_lower:
        return "You're welcome 😊"

    # -------- CUSTOM KNOWLEDGE --------
    custom = search_knowledge(query)
    if custom:
        return custom

    try:
        docs = db.similarity_search(query, k=3)

        if not docs:
            return "NOT_FOUND"

        context = " ".join([doc.page_content for doc in docs])

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are an EV assistant.

Use ONLY the context.
If not found return: NOT_FOUND

Context:
{context}

Question:
{query}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content.strip()

        return answer if answer else "NOT_FOUND"

    except:
        return "NOT_FOUND"