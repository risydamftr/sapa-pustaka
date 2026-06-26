from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

reader = PdfReader(
    "knowledge/SK 157 2025 Instrumen Akreditasi Perpustakaan SD MI.pdf"
)

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="akreditasi_perpustakaan_v2"
)

for page_num, page in enumerate(reader.pages):

    text = page.extract_text()

    if not text:
        continue

    embedding = model.encode(text).tolist()

    collection.add(
        ids=[f"page_{page_num+1}"],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "page": page_num + 1,
                "source": "instrumen_akreditasi.pdf"
            }
        ]
    )

print("Indexing selesai")