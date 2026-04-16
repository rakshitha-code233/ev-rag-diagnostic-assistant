import os
import re
from typing import List

from dotenv import load_dotenv
from groq import Groq

from rag import format_citations, format_context, retrieve_manual_chunks


load_dotenv()


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
