import os
import re
import fitz
import chromadb

from sentence_transformers import SentenceTransformer

# ==========================================
# CONFIG
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWLEDGE_FOLDER = os.path.join(BASE_DIR, "knowledge")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

COLLECTION_NAME = "akreditasi_perpustakaan_v8"

# ==========================================
# EMBEDDING & CHROMA RESET
# ==========================================

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

# 🔥 Skenario hapus total index lama agar tidak duplikat
print(f"Membersihkan index lama pada collection: {COLLECTION_NAME}...")
try:
    client.delete_collection(COLLECTION_NAME)
    print("✅ Sukses menghapus index lama.")
except:
    print("ℹ️ Collection tidak ditemukan / sudah bersih. Membuat baru...")

# Selalu gunakan create_collection setelah delete agar mendapatkan objek yang fresh
collection = client.create_collection(name=COLLECTION_NAME)

# ==========================================
# LIBRARY TYPE DETECTION
# ==========================================
def detect_library_type(filename):
    name = filename.lower()

    if "perpustakaan khusus lembaga pemerintah" in name: return "KHUSUS_PEMERINTAH"
    if "perpustakaan khusus lembaga nonpemerintah" in name: return "KHUSUS_NONPEMERINTAH"
    if "perpustakaan rumah ibadah" in name: return "RUMAH_IBADAH"
    if "perpustakaan provinsi" in name: return "PROVINSI"
    if "perpustakaan kab kota" in name: return "KABUPATEN_KOTA"
    if "perpustakaan kecamatan" in name: return "KECAMATAN"
    if "perpustakaan desa kelurahan" in name: return "DESA_KELURAHAN"
    if "perpustakaan universitas" in name: return "UNIVERSITAS"
    if "perpustakaan institut sekolah tinggi politeknik" in name: return "POLITEKNIK"
    if "perpustakaan akademi dan akademi komunitas" in name: return "AKADEMI_KOMUNITAS"
    if "paud" in name: return "PAUD"
    if "slb" in name: return "SLB"
    if "smp" in name: return "SMP"
    if "sma" in name: return "SMA"
    if "sd" in name: return "SD"

    return "UNKNOWN"

# ==========================================
# PDF EXTRACTION
# ==========================================
def extract_full_document(doc):
    texts = []
    for page in doc:
        page_text = page.get_text("text")
        page_text = re.sub(r"\n{3,}", "\n\n", page_text)
        texts.append(page_text)
    return "\n".join(texts)

# ==========================================
# PARSER (UPDATED)
# ==========================================
def parse_akreditasi_document(text):
    lines = text.split("\n")
    chunks = []

    current_component = "UNKNOWN_COMPONENT"
    current_subcomponent = "UNKNOWN_SUBCOMPONENT"
    
    # Variabel pelacak bantuan untuk strategi Backfill
    last_valid_subcomponent = "UNKNOWN_SUBCOMPONENT"
    last_valid_component = "UNKNOWN_COMPONENT"
    
    current_indicator = None
    current_content = []

    component_pattern = re.compile(r"^[A-Z]\.\s+Komponen", re.IGNORECASE)
    subcomponent_pattern = re.compile(r"^\d+\.\d+\s+")
    indicator_pattern = re.compile(r"^\d+\.\s+")

    has_started_instrument = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # 1. Deteksi Komponen Baru
        if component_pattern.match(line):
            has_started_instrument = True
            current_component = line
            last_valid_component = line
            current_subcomponent = "UNKNOWN_SUBCOMPONENT"  # Reset subkomponen saat masuk komponen baru
            continue

        if not has_started_instrument:
            continue

        # 2. Deteksi Subkomponen Baru
        if subcomponent_pattern.match(line):
            current_subcomponent = line
            last_valid_subcomponent = line
            continue

        # 3. Deteksi Indikator Baru
        if indicator_pattern.match(line) and not subcomponent_pattern.match(line):
            # Simpan chunk sebelumnya jika sudah ada indikator yang terkumpul
            if current_indicator:
                # Logika Backfill: Jika subkomponen/komponen hilang karena ganti halaman PDF, gunakan yang sebelumnya
                final_sub = current_subcomponent if current_subcomponent != "UNKNOWN_SUBCOMPONENT" else last_valid_subcomponent
                final_comp = current_component if current_component != "UNKNOWN_COMPONENT" else last_valid_component
                
                chunks.append({
                    "component": final_comp,
                    "subcomponent": final_sub,
                    "indicator": current_indicator.strip(),
                    "content": "\n".join(current_content).strip()
                })

            current_indicator = line
            current_content = [] 
            continue

        # 4. Pengumpulan Teks (Bisa berupa kelanjutan kalimat Indikator atau bagian Konten)
        if current_indicator:
            # Mengatasi kalimat indikator yang terpotong ke baris baru:
            # Jika teks belum menyentuh "Pilihan Jawaban" atau "Bukti Fisik", gabungkan ke baris indikator utama dengan spasi
            if not current_content and not re.match(r"^(Pilihan\s*Jawaban|Bukti\s*fisik|Keterangan)", line, re.IGNORECASE):
                current_indicator += " " + line
            else:
                current_content.append(line)

    # Masukkan chunk terakhir setelah loop selesai
    if current_indicator and has_started_instrument:
        final_sub = current_subcomponent if current_subcomponent != "UNKNOWN_SUBCOMPONENT" else last_valid_subcomponent
        final_comp = current_component if current_component != "UNKNOWN_COMPONENT" else last_valid_component
        
        chunks.append({
            "component": final_comp,
            "subcomponent": final_sub,
            "indicator": current_indicator.strip(),
            "content": "\n".join(current_content).strip()
        })

    return chunks

# ==========================================
# RUN INDEXING
# ==========================================
total_chunks = 0

for filename in os.listdir(KNOWLEDGE_FOLDER):
    if not filename.endswith(".pdf"):
        continue

    filepath = os.path.join(KNOWLEDGE_FOLDER, filename)
    library_type = detect_library_type(filename)

    print(f"\nPROCESSING : {filename}")

    try:
        doc = fitz.open(filepath)
        full_text = extract_full_document(doc)
        parsed_chunks = parse_akreditasi_document(full_text)

        if not parsed_chunks:
            print(f"SKIPPED -> {filename} tidak berisi data komponen instrumen.")
            continue

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for idx, chunk in enumerate(parsed_chunks):
            text_for_embedding = f"""Jenis Perpustakaan:
{library_type}

Komponen:
{chunk['component']}

Subkomponen:
{chunk['subcomponent']}

Indikator:
{chunk['indicator']}

Konten:
{chunk['content']}"""

            embedding = model.encode(text_for_embedding).tolist()

            ids.append(f"{filename}_{idx}")
            documents.append(text_for_embedding)
            embeddings.append(embedding)
            metadatas.append({
                "source": filename,
                "library_type": library_type,
                "component": chunk["component"],
                "subcomponent": chunk["subcomponent"],
                "indicator": chunk["indicator"]
            })

            total_chunks += 1

        # Tambahkan data ke koleksi baru yang bersih
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(f"SUCCESS -> {len(parsed_chunks)} indikator masuk database.")

    except Exception as e:
        print(f"ERROR {filename}: {e}")

# ==========================================
# SUMMARY
# ==========================================
print("\n" + "="*60)
print("INDEXING COMPLETE (ALL OLD DATA WIPED)")
print("="*60)
print(f"TOTAL CHUNKS IN DATABASE : {total_chunks}")