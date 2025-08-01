import os
import pickle
from typing import List, Tuple

import faiss
from sentence_transformers import SentenceTransformer

# Path inside backend folder to persist the FAISS index & metadata
DATA_DIR = os.path.join(os.path.dirname(__file__), "faiss_store")
INDEX_FILE = os.path.join(DATA_DIR, "faiss.index")
META_FILE = os.path.join(DATA_DIR, "documents.pkl")

# Re-use same model throughout
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
from typing import Optional

_model: Optional[SentenceTransformer] = None
_index: Optional[faiss.IndexFlatIP] = None
_documents: Optional[List[str]] = None


def _ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def build_index(documents: List[str], rebuild: bool = False) -> None:
    """Builds a FAISS index from the supplied documents and saves it.

    Args:
        documents: List of raw text strings.
        rebuild: If False and existing index exists, do nothing.
    """
    _ensure_dirs()

    if os.path.exists(INDEX_FILE) and not rebuild:
        print("[KnowledgeBase] Index already exists – skipping rebuild. Use rebuild=True to force.")
        return

    if not documents:
        raise ValueError("No documents supplied to build_index")

    print(f"[KnowledgeBase] Building FAISS index from {len(documents)} documents…")

    # Embed documents
    model = _get_model()
    embeddings = model.encode(documents, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity with normalized vectors
    index.add(embeddings)

    # Persist
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(documents, f)

    print("[KnowledgeBase] Index built & saved to", INDEX_FILE)


def load_index() -> Tuple[faiss.IndexFlatIP, List[str]]:
    """Loads FAISS index + documents list from disk. Builds error if missing."""
    global _index, _documents

    if _index is not None and _documents is not None:
        return _index, _documents

    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError("FAISS index not found – run build_index() first")

    _index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        _documents = pickle.load(f)

    return _index, _documents


def similarity_search(query: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """Returns top_k (document, score) tuples similar to query."""
    index, documents = load_index()
    model = _get_model()

    query_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, indices = index.search(query_emb, top_k)
    scores = scores[0]
    indices = indices[0]

    results: List[Tuple[str, float]] = []
    for idx, score in zip(indices, scores):
        if idx < len(documents):
            results.append((documents[idx], float(score)))
    return results


if __name__ == "__main__":
    # Simple CLI test
    sample_docs = [
        "नमस्ते! मेरा नाम आलिया है।",
        "मैं हिंदी सीख रहा हूँ क्योंकि मुझे भारतीय संस्कृति पसंद है।",
        "दिल्ली भारत की राजधानी है।",
    ]
    build_index(sample_docs, rebuild=True)
    print(similarity_search("राजधानी", 2)) 