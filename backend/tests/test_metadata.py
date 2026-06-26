#import os
#import chromadb

#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#CHROMA_PATH = os.path.join(BASE_DIR, "..", "chroma_db")

#client = chromadb.PersistentClient(path=CHROMA_PATH)
#collection = client.get_collection("akreditasi_perpustakaan_v8")

# 💡 Minta ChromaDB khusus mengambil sampel data yang library_type-nya 'Universitas'
#data_universitas = collection.get(
#    where={"library_type": "UNIVERSITAS"},
#    limit=10
#)

#print(f"Jumlah data UNIVERSITAS yang ditemukan: {len(data_universitas['documents'])} chunk")

#if data_universitas['documents']:
#    print("\n==================== [ 10 CONTOH DATA SMA ] ====================")
    
    # Melakukan looping untuk menggabungkan ids, metadatas, dan documents
#    for i, (idx, meta, doc) in enumerate(zip(data_universitas["ids"], data_universitas["metadatas"], data_universitas["documents"])):
#        print(f"\n--- CHUNK KE-{i+1} ---")
#        print("ID   :", idx)
#        print("META :", meta)
#        print("DOC  :", doc[:1000]) # Membatasi teks dokumen agar tidak terlalu panjang di terminal
#        print("-" * 40)
#else:
#    print("❌ Data Universitas belum masuk...")

import os
import chromadb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "..", "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("akreditasi_perpustakaan_v8")

# 1. Ambil semua data Universitas tanpa batasan limit dahulu
all_data = collection.get(
    where={"library_type": "SMA"}
)

total_data = len(all_data['documents'])
print(f"Total seluruh data SMA: {total_data} chunk")

if total_data > 0:
    print("\n==================== [ 10 CHUNK TERBAWAH ] ====================")
    
    # 2. Slicing [-10:] untuk mengambil 10 data terakhir dari list
    last_ids = all_data["ids"][-10:]
    last_metas = all_data["metadatas"][-10:]
    last_docs = all_data["documents"][-10:]
    
    # Hitung posisi index aslinya di database agar penomoran chunk sesuai
    start_index = max(0, total_data - 10)

    for i, (idx, meta, doc) in enumerate(zip(last_ids, last_metas, last_docs)):
        print(f"\n--- CHUNK KE-{start_index + i + 1} (Urutan Terakhir) ---")
        print("ID   :", idx)
        print("META :", meta)
        print("DOC  :", doc[:1000])
        print("-" * 40)
else:
    print("❌ Data Universitas belum masuk...")
