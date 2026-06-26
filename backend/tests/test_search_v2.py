import sys
import os

# ==========================================
# 1. SET PROJECT ROOT (IMPORTANT FIX)
# ==========================================
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
sys.path.append(BASE_DIR)

# ==========================================
# 2. IMPORT RESMI DARI SERVICES KAMU
# ==========================================
# Panggil fungsi search yang sudah include Context Enrichment + FlashRank Reranker
from services.rag_services import search_documents

# ==========================================
# 3. SET QUESTION FOR TESTING
# ==========================================
question = "Apa saja komponen pengelolaan perpustakaan SD?"

print("=" * 80)
print(f"RUNNING RAG SEARCH TEST")
print("=" * 80)
print(f"QUESTION: {question}")
print("=" * 80)

# ==========================================
# 4. JALANKAN PENCARIAN
# ==========================================
# Fungsi ini otomatis mendeteksi library_type, meng-embed, query 15 docs, lalu me-rerank menjadi 5 docs
results = search_documents(question)

# ==========================================
# 5. TAMPILKAN HASILNYA (Otomatis Terurut Berdasarkan Skor Rerank)
# ==========================================
documents = results["documents"]
metadatas = results["metadata"]
scores = results["distances"]  # Ingat, di rag_services nilainya sekarang adalah score FlashRank

if not documents:
    print("\n[!] Tidak ada dokumen yang ditemukan.")
else:
    for i in range(len(documents)):
        print("\n" + "=" * 80)
        print(f"HASIL RE-RANK KE-{i+1}")
        print("=" * 80)

        meta = metadatas[i]

        print(f"LIBRARY TYPE : {meta['library_type']}")
        print(f"PAGE         : {meta['page']}")
        print(f"RERANK SCORE : {scores[i]:.4f} (Makin besar makin relevan)")
        print(f"SOURCE FILE  : {meta['source']}")
        print("-" * 80)
        print("TEXT PREVIEW :")
        print(documents[i])
        print("=" * 80)