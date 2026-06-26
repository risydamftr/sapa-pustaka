import os
import chromadb

from sentence_transformers import SentenceTransformer
from flashrank import Ranker, RerankRequest

from services.library_type_services import detect_library_type_question

# ==================================================
# CHROMA CONFIG
# ==================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("akreditasi_perpustakaan_v8")

ranker = Ranker()

# ==================================================
# SEARCH WITH HIERARCHICAL RETRIEVAL
# ==================================================
def search_documents(question: str):
    library_type = detect_library_type_question(question)

    print("\n==============================")
    print("DETEKSI AWAL USER QUESTION")
    print("LIBRARY TYPE:", library_type)
    print("==============================\n")

    if library_type and library_type != "UNKNOWN":
        library_type = library_type.upper()

    # ========================================
    # QUERY ENRICHMENT
    # ========================================
    enriched_query = question
    if library_type != "UNKNOWN":
        enriched_query += f"\nJenis Perpustakaan: {library_type}"

    # ========================================
    # EMBEDDING GENERATION
    # ========================================
    embedding = model.encode(
        enriched_query,
        normalize_embeddings=True
    ).tolist()

    where_filter = {}
    if library_type != "UNKNOWN":
        where_filter = {"library_type": {"$eq": library_type}}

    # ========================================
    # TAHAP 1: DETEKSI KOMPONEN (HYBRID)
    # ========================================
    detected_component = None
    component_keyword = None  
    q_low = question.lower()

    # PERBAIKAN 1: Memperluas keyword matching agar mencakup variasi kata umum
    if "koleksi" in q_low or "pelestarian" in q_low or "bahan pustaka" in q_low:
        detected_component = "A. Komponen Koleksi Perpustakaan"
        component_keyword = "Komponen Koleksi"
    elif "sarana" in q_low or "prasarana" in q_low or "gedung" in q_low or "ruang" in q_low or "perabot" in q_low or "perangkat it" in q_low:
        detected_component = "B. Komponen Sarana dan Prasarana Perpustakaan"
        component_keyword = "Sarana dan Prasarana"
    elif "layanan" in q_low or "pelayanan" in q_low or "sirkulasi" in q_low:
        detected_component = "C. Komponen Pelayanan Perpustakaan"
        component_keyword = "Pelayanan Perpustakaan"
    elif "tenaga" in q_low or "pustakawan" in q_low or "kepala" in q_low or "kompetensi" in q_low:
        detected_component = "D. Komponen Tenaga Perpustakaan"
        component_keyword = "Tenaga Perpustakaan"
    elif "penyelenggaraan" in q_low or "organisasi" in q_low or "manajemen" in q_low:
        detected_component = "E. Komponen Penyelenggaraan Perpustakaan"
        component_keyword = "Penyelenggaraan"
    elif "pengelolaan" in q_low or "anggaran" in q_low or "inovasi" in q_low:
        detected_component = "F. Komponen Pengelolaan Perpustakaan"
        component_keyword = "Pengelolaan Perpustakaan"

    is_detected_by_vector = False
    if not detected_component:
        print("🤖 Keyword tidak cocok, mendeteksi komponen via Vector Search...")
        query_params = {"query_embeddings": [embedding], "n_results": 1}
        if where_filter:
            query_params["where"] = where_filter

        initial_chroma = collection.query(**query_params)
        if initial_chroma["metadatas"] and initial_chroma["metadatas"][0]:
            detected_component = initial_chroma["metadatas"][0][0].get("component")
            if detected_component:
                component_keyword = detected_component[:15]
                is_detected_by_vector = True
    else:
        print(f"📌 Terdeteksi via Rule Keyword!")

    print(f"🎯 HASIL AKHIR DETEKSI -> Komponen: '{detected_component}'")

    # ========================================
    # TAHAP 2: RETRIEVE DAN FILTER DATA
    # ========================================
    # PERBAIKAN 2: Jika terdeteksi via vector (terutama untuk UNKNOWN), jangan lakukan penguncian komponen total 
    # karena rawan salah kunci. Langsung ambil fallback data dengan limit besar.
    if not detected_component or (is_detected_by_vector and library_type == "UNKNOWN"):
        print("⚠️ Menggunakan fallback pencarian global (Anti-Kunci Komponen).")
        fallback_params = {"query_embeddings": [embedding], "n_results": 30}
        if where_filter:
            fallback_params["where"] = where_filter
            
        fallback_results = collection.query(**fallback_params)
        filtered_docs = fallback_results["documents"][0] if fallback_results["documents"] else []
        filtered_metadata = fallback_results["metadatas"][0] if fallback_results["metadatas"] else []
    else:
        if library_type != "UNKNOWN":
            fetch_where = {"library_type": {"$eq": library_type}}
        else:
            fetch_where = None
            
        component_data = collection.get(where=fetch_where, limit=150)
        all_docs = component_data["documents"] if component_data["documents"] else []
        all_metadatas = component_data["metadatas"] if component_data["metadatas"] else []
        
        filtered_docs = []
        filtered_metadata = []
        search_term = component_keyword if component_keyword else detected_component
        
        for doc, meta in zip(all_docs, all_metadatas):
            meta_component = meta.get("component", "")
            if search_term.lower() in meta_component.lower():
                filtered_docs.append(doc)
                filtered_metadata.append(meta)
        
        print(f"📚 Berhasil menarik total {len(filtered_docs)} seluruh indikator dalam komponen.")
        
        if not filtered_docs:
            return {"documents": [], "metadata": [], "distances": []}

    # ========================================
    # TAHAP 3: RE-RANKING DENGAN FLASHRANK
    # ========================================
    passages = [
        {"id": idx, "text": doc, "metadata": meta}
        for idx, (doc, meta) in enumerate(zip(filtered_docs, filtered_metadata))
    ]

    rerank_request = RerankRequest(query=question, passages=passages)
    reranked = ranker.rerank(rerank_request)

    final_docs = []
    final_meta = []
    final_scores = []

    for item in reranked:
        final_docs.append(item.get("text", ""))
        final_meta.append(item.get("metadata", {}))
        final_scores.append(item.get("score", 0))

    # PERBAIKAN 3: Proteksi Threshold Nilai Rerank
    # Jika skor tertinggi di bawah 0.65, artinya dokumen benar-benar tidak nyambung (seperti mencari Universitas di data SD).
    if final_scores and final_scores[0] < 0.65:
        print(f"🛑 Rerank score terlalu rendah ({final_scores[0]:.4f}). Membersihkan context...")
        return {"documents": [], "metadata": [], "distances": []}

    print("\n=== HASIL AKHIR CONTEXT RAG ===")
    for i, doc in enumerate(final_docs[:3]):
        if i < len(final_scores):
            print(f"\nRANK {i+1} (Score: {final_scores[i]:.4f})")
            print(f"Indikator: {final_meta[i].get('indicator', '-')}")

    return {
        "documents": final_docs,
        "metadata": final_meta,
        "distances": final_scores
    }