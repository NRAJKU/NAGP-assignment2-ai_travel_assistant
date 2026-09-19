from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
VECTOR_DIR = ROOT / "data" / "vectorstore"
EMBED_MODEL = "BAAI/bge-m3"


class BGEEmbeddings(Embeddings):
    """LangChain Embeddings adapter for BAAI/bge-m3."""

    def __init__(self, model_name: str = EMBED_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.tolist()


_embeddings = BGEEmbeddings()
_vectorstore: FAISS | None = None


def get_vectorstore() -> FAISS:
    """Load the FAISS knowledge base lazily and cache it."""
    global _vectorstore

    if _vectorstore is None:
        index_file = VECTOR_DIR / "index.faiss"

        if not index_file.exists():
            raise RuntimeError(
                "Knowledge base is not built. "
                "Run: python scripts/ingest.py"
            )

        _vectorstore = FAISS.load_local(
            str(VECTOR_DIR),
            _embeddings,
            allow_dangerous_deserialization=True,
        )

    return _vectorstore


@tool
def search_singapore_knowledge_base(query: str) -> str:
    """
    Search stable Singapore destination knowledge.

    Use this tool for attractions, neighbourhoods, transport, culture,
    food, local experiences, and itinerary ideas.

    Do not use this tool for live weather, current forecasts,
    exchange rates, hotel availability, flight availability,
    or restaurant reservation availability.
    """
    try:
        docs = get_vectorstore().similarity_search(
            query,
            k=5,
        )
    except Exception as exc:
        return f"KNOWLEDGE_BASE_ERROR: {exc}"

    if not docs:
        return (
            "KNOWLEDGE_BASE_EMPTY: "
            "No relevant destination content was retrieved."
        )

    blocks: list[str] = []

    for index, doc in enumerate(docs, start=1):
        source_title = doc.metadata.get(
            "source_title",
            "Unknown",
        )
        source_url = doc.metadata.get(
            "source_url",
            "",
        )

        blocks.append(
            f"[SOURCE {index}] {source_title}\n"
            f"URL: {source_url}\n"
            f"CONTENT:\n{doc.page_content}"
        )

    return "\n\n".join(blocks)