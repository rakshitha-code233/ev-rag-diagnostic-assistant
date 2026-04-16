import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# ------------------ LOAD API ------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None

# ------------------ LOAD MODEL ------------------
model = None

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
    def get_answer(user_query):
        manual_answer = search_manual(user_query)

        if manual_answer:
            return manual_answer
        else:
            return "I couldn’t find this in the manual, but here’s an AI-based answer:\n\n" + get_ai_answer(user_query)
    # 5. AI answer
    return get_ai_answer(query)
    print("Manual Answer:", manual_answer)


# ------------------ RAG OVERRIDES ------------------
from typing import List

from rag import format_citations, format_context, retrieve_manual_chunks


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "car",
    "check",
    "do",
    "does",
    "ev",
    "for",
    "how",
    "i",
    "is",
    "it",
    "level",
    "locate",
    "located",
    "long",
    "manual",
    "me",
    "model",
    "my",
    "of",
    "on",
    "port",
    "should",
    "take",
    "tell",
    "tesla",
    "the",
    "to",
    "type",
    "types",
    "what",
    "where",
    "with",
}


def normalize_token(token: str) -> str:
    token = token.lower()
    for suffix in ("ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            token = token[: -len(suffix)]
            break
    return token


def extract_keywords(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {
        normalize_token(token)
        for token in tokens
        if len(token) >= 3 and normalize_token(token) not in STOPWORDS
    }


def select_relevant_chunks(query: str):
    relevant_chunks = []
    query_terms = extract_keywords(query)
    is_definition_query = bool(re.match(r"^\s*what\s+(is|are)\b", query.lower()))

    for chunk in retrieve_manual_chunks(query):
        chunk_terms = extract_keywords(chunk.text)
        overlap = query_terms & chunk_terms

        if not query_terms:
            continue

        if is_definition_query and chunk.score < 0.55:
            continue

        if len(overlap) >= 2:
            relevant_chunks.append(chunk)
            continue

        if len(query_terms) <= 2 and overlap and chunk.score >= 0.6:
            relevant_chunks.append(chunk)

    return relevant_chunks


def handle_greetings(query: str) -> str | None:
    normalized = query.lower().strip()
    if normalized in {"hi", "hello", "hey"}:
        return "Hello. Ask me about EV diagnostics and I will answer from the indexed manuals with page citations."
    if "thank" in normalized:
        return "You're welcome."
    return None


def get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def build_manual_only_prompt(query: str, context: str) -> List[dict]:
    system_prompt = (
        "You are an EV diagnostic assistant for service technicians. "
        "Answer only from the provided repair manual excerpts. "
        "You may answer diagnostic or owner-manual questions when the excerpts support them. "
        "If the excerpts answer only part of the question, answer the supported parts and clearly say what is missing. "
        "Prefer step-by-step procedures, safety checks, and exact manual guidance. "
        "Cite source numbers inline like [Source 1] when you use them."
    )
    user_prompt = (
        f"Technician question:\n{query}\n\n"
        f"Manual excerpts:\n{context}\n\n"
        "Respond with:\n"
        "1. A concise answer.\n"
        "2. A 'Procedure' section with numbered steps only when the excerpts contain steps.\n"
        "3. A 'Citations' section mapping each used source number to its manual/page."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_extract_answer(query: str) -> str:
    chunks = select_relevant_chunks(query)
    if not chunks:
        return (
            "I could not find relevant guidance in the indexed manuals yet. "
            "Upload one or more EV repair manuals, then ask again."
        )

    procedure_lines = [f"{index}. {chunk.text}" for index, chunk in enumerate(chunks, start=1)]
    citations = format_citations(chunks)
    return (
        "I found relevant manual guidance.\n\n"
        "Procedure:\n"
        + "\n".join(procedure_lines)
        + "\n\nCitations:\n"
        + "\n".join(f"- {citation}" for citation in citations)
    )


def get_answer(query: str) -> str:
    greeting = handle_greetings(query)
    if greeting:
        return greeting

    chunks = select_relevant_chunks(query)
    if not chunks:
        return (
            "I could not find a matching answer in the indexed manuals. "
            "Try naming the vehicle, system, symptom, or DTC, or upload the relevant manual first."
        )

    context = format_context(chunks)
    citations = format_citations(chunks)
    client = get_groq_client()

    if client is None:
        return build_extract_answer(query)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=build_manual_only_prompt(query, context),
            temperature=0.2,
        )
        answer = response.choices[0].message.content.strip()
    except Exception:
        return build_extract_answer(query)

    if "Citations:" not in answer:
        answer = answer + "\n\nCitations:\n" + "\n".join(f"- {citation}" for citation in citations)

    return answer
