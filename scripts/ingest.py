from pathlib import Path
import shutil

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
VECTOR = ROOT / "data" / "vectorstore"
EMBED_MODEL = "BAAI/bge-m3"


class BGEEmbeddings(Embeddings):
    def __init__(self, model_name=EMBED_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, text):
        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()


docs = []

for path in sorted(RAW.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    title = path.stem
    url = ""
    source_type = ""

    for line in text.splitlines()[:8]:
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("source_url:"):
            url = line.split(":", 1)[1].strip()
        elif line.startswith("source_type:"):
            source_type = line.split(":", 1)[1].strip()

    docs.append(
        Document(
            page_content=text,
            metadata={
                "source_title": title,
                "source_url": url,
                "source_type": source_type,
                "file_name": path.name,
            },
        )
    )

if len(docs) < 3:
    raise RuntimeError("At least three source documents are required.")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=150,
    separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "]
)

chunks = splitter.split_documents(docs)

emb = BGEEmbeddings(EMBED_MODEL)

if VECTOR.exists():
    shutil.rmtree(VECTOR)

VECTOR.mkdir(parents=True, exist_ok=True)

FAISS.from_documents(chunks, emb).save_local(str(VECTOR))

print(f"Documents: {len(docs)}")
print(f"Chunks: {len(chunks)}")
print(f"Vector store: {VECTOR}")