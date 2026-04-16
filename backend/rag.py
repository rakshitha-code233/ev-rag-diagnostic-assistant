import json
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import fitz
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data" / "manuals"
INDEX_DIR = BASE_DIR / "rag_store"
INDEX_FILE = INDEX_DIR / "manual_index.faiss"
METADATA_FILE = INDEX_DIR / "manual_chunks.json"
DEFAULT_TOP_K = 4
MIN_CHUNK_CHARS = 120


@dataclass
class RetrievedChunk:
    manual: str
    page: int
    text: str
    score: float

    @property
    def citation(self) -> str:
        return f"{self.manual} p.{self.page}"


_model: Optional[SentenceTransformer] = None


class LocalHashingEmbedder:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def encode(
        self,
        texts: List[str],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        del show_progress_bar
        vectors = np.zeros((len(texts), self.dimension), dtype="float32")

        for row, text in enumerate(texts):
            tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
            if not tokens:
                continue

            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                bucket = int.from_bytes(digest[:4], "little") % self.dimension
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                vectors[row, bucket] += sign

        if normalize_embeddings:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            vectors = vectors / norms

        if convert_to_numpy:
            return vectors
        return vectors.tolist()


def get_embedding_model():
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            _model = LocalHashingEmbedder()
    return _model


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def list_manual_files() -> List[Path]:
    ensure_directories()
    return sorted(DATA_DIR.glob("*.pdf"))


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_page_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    cleaned = clean_text(text)
    if len(cleaned) < MIN_CHUNK_CHARS:
        return []

    chunks: List[str] = []
    start = 0
    text_length = len(cleaned)

    while start < text_length:
        end = min(text_length, start + chunk_size)
        if end < text_length:
            boundary = cleaned.rfind(" ", start, end)
            if boundary > start + (chunk_size // 2):
                end = boundary

        chunk = cleaned[start:end].strip()
        if len(chunk) >= MIN_CHUNK_CHARS:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - overlap, start + 1)

    return chunks


def extract_chunks_from_pdf(pdf_path: Path) -> List[Dict[str, object]]:
    doc = fitz.open(pdf_path)
    chunks: List[Dict[str, object]] = []

    try:
        for page_number, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            for chunk_index, chunk_text in enumerate(split_page_text(page_text)):
                chunks.append(
                    {
                        "id": f"{pdf_path.stem}-p{page_number}-c{chunk_index}",
                        "manual": pdf_path.name,
                        "page": page_number,
                        "text": chunk_text,
                    }
                )
    finally:
        doc.close()

    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, 384), dtype="float32")

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.astype("float32")


def build_manual_index() -> Dict[str, object]:
    ensure_directories()
    manual_files = list_manual_files()
    all_chunks: List[Dict[str, object]] = []

    for pdf_path in manual_files:
        all_chunks.extend(extract_chunks_from_pdf(pdf_path))

    if not all_chunks:
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
        if METADATA_FILE.exists():
            METADATA_FILE.unlink()
        return {"manuals_indexed": 0, "chunks_indexed": 0}

    embeddings = embed_texts([chunk["text"] for chunk in all_chunks])
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(INDEX_FILE))

    with METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(all_chunks, file, ensure_ascii=True, indent=2)

    return {
        "manuals_indexed": len(manual_files),
        "chunks_indexed": len(all_chunks),
    }


def load_manual_index() -> Optional[Dict[str, object]]:
    if not INDEX_FILE.exists() or not METADATA_FILE.exists():
        return None

    index = faiss.read_index(str(INDEX_FILE))
    with METADATA_FILE.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    return {"index": index, "metadata": metadata}


def retrieve_manual_chunks(query: str, top_k: int = DEFAULT_TOP_K) -> List[RetrievedChunk]:
    store = load_manual_index()
    if store is None:
        return []

    query_embedding = embed_texts([query])
    if query_embedding.size == 0:
        return []

    distances, indices = store["index"].search(query_embedding, top_k)
    retrieved: List[RetrievedChunk] = []

    for score, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(store["metadata"]):
            continue

        item = store["metadata"][idx]
        if score < 0.25:
            continue

        retrieved.append(
            RetrievedChunk(
                manual=str(item["manual"]),
                page=int(item["page"]),
                text=str(item["text"]),
                score=float(score),
            )
        )

    return deduplicate_chunks(retrieved)


def deduplicate_chunks(chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
    seen = set()
    unique_chunks: List[RetrievedChunk] = []

    for chunk in chunks:
        key = (chunk.manual, chunk.page, chunk.text[:120])
        if key in seen:
            continue
        seen.add(key)
        unique_chunks.append(chunk)

    return unique_chunks


def format_context(chunks: List[RetrievedChunk]) -> str:
    blocks = []
    for idx, chunk in enumerate(chunks, start=1):
        blocks.append(f"[Source {idx}] {chunk.citation}\n{chunk.text}")
    return "\n\n".join(blocks)


def format_citations(chunks: List[RetrievedChunk]) -> List[str]:
    citations: List[str] = []
    seen = set()
    for chunk in chunks:
        if chunk.citation in seen:
            continue
        seen.add(chunk.citation)
        citations.append(chunk.citation)
    return citations
