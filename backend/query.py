import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np  
from dotenv import load_dotenv
import re

load_dotenv()

documents = []

# ------------------ LOAD MODEL ------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ------------------ LOAD FAISS ------------------

def load_index():
    if os.path.exists("faiss_index.index"):
        return faiss.read_index("faiss_index.index")
    return None

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

    import faiss
    import os

    if not os.path.exists("faiss_index.index"):
        return None

    index = faiss.read_index("faiss_index.index")

    query_vector = model.encode([query])
    D, I = index.search(query_vector, k=8)

    with open("stored_chunks.txt", "r", encoding="utf-8") as f:
        chunks = f.readlines()

    query_words = query.lower().split()

    best_chunk = None
    best_score = 0

    for i in I[0]:
        if i < len(chunks):

            chunk = chunks[i].strip().lower()

            # ❌ REMOVE IRRELEVANT CONTENT
            if "camera" in chunk:
                continue
            if "key card" in chunk:
                continue
            if "navigation" in chunk:
                continue

            score = sum(1 for word in query_words if word in chunk)

            # 🔥 MUST MATCH CORE WORD
            if "charge" in query and "charge" not in chunk:
                continue

            if score > best_score and score >= 2:
                best_score = score
                best_chunk = chunk

    if best_chunk:
        return best_chunk.capitalize()

    return None
# ------------------ AI FALLBACK ------------------
def handle_special_cases(query):
    q = query.lower()

    if "not starting" in q or "won't start" in q:
        return "⚠️ Possible issues:\n- Battery low\n- Key not detected\n- System fault\n\nCheck battery and restart vehicle."

    if "parts" in q:
        return "❌ Not found in manual.\n\nDo you want AI answer? (type: yes)"

    return None


# ------------------ MAIN FUNCTION ------------------
def get_answer(query):

    # 1. Greeting
    greet = handle_greetings(query)
    if greet:
        return greet

    # 2. Special cases
    special = handle_special_cases(query)
    if special:
        return special

    # 3. Manual search ONLY
    manual = search_manual(query)
    if manual:
        return f"📘 From Manual:\n\n{manual}"

    # 4. STRICT MODE (NO AI)
    return "❌ Answer not found in uploaded manual."