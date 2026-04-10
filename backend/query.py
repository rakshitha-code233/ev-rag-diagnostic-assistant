import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# ------------------ LOAD API ------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------ LOAD MODEL ------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------ LOAD FAISS ------------------
if os.path.exists("faiss_index.index"):
    index = faiss.read_index("faiss_index.index")
else:
    index = None

# ------------------ LOAD DOCUMENTS ------------------
file_path = os.path.join(os.path.dirname(__file__), "documents.txt")

with open(file_path, "r", encoding="utf-8") as f:
    documents = f.readlines()

# ------------------ GREETINGS ------------------
def handle_greetings(query):
    q = query.lower().strip()
    if q in ["hi", "hello", "hey"]:
        return "Hello! 👋 Ask me about EV diagnostics."
    if "thank" in q:
        return "You're welcome 😊"
    return None

# ------------------ SEARCH MANUAL ------------------
def search_manual(query):
    if index is None:
        return None

    query_vector = model.encode([query])
    D, I = index.search(query_vector, k=2)

    # 🔥 STRICT FILTER (important)
    if D[0][0] > 0.6:
        return None

    results = []
    for i in I[0]:
        if i < len(documents):
            results.append(documents[i].strip())

    return "\n\n".join(results)

# ------------------ AI FALLBACK ------------------
def get_ai_answer(query):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ✅ updated model
            messages=[
                {"role": "system", "content": "You are an EV diagnostic assistant."},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
    
def handle_special_cases(query):
    q = query.lower()

    if "not starting" in q or "won't start" in q:
        return "⚠️ Possible issues:\n- Battery low\n- Key not detected\n- System fault\n\nCheck battery and restart vehicle."

    if "parts" in q:
        return "❌ Not found in manual.\n\nDo you want AI answer? (type: yes)"

    return None

# ------------------ MAIN FUNCTION ------------------
def get_answer(query, use_ai=False):

    # 1. Greeting
    greet = handle_greetings(query)
    if greet:
        return greet

    # 2. Special cases
    special = handle_special_cases(query)
    if special:
        return special

    # 3. Manual search
    manual = search_manual(query)
    if manual:
        return f"📘 From Manual:\n\n{manual}"

    # 4. Ask for AI
    if not use_ai:
        return "❌ Not found in manual.\n\nDo you want AI answer? (type: yes)"

    # 5. AI answer
    return get_ai_answer(query)