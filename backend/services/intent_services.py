from services.library_type_services import detect_library_type_question

def classify_intent(question):
    q = question.lower().strip()
    q_clean = q.replace("?", "").replace("!", "").replace(",", "")

    # ==========================================
    # 1. INTENT: GREETING (SAPAAN)
    # ==========================================
    greeting_words = [
        "halo", "hai", "hi", "hey", "pagi", "siang", "sore", "malam",
        "selamat pagi", "selamat siang", "selamat sore", "selamat malam"
    ]
    
    bot_profile_queries = [
        "siapa kamu", "apa itu sapa pustaka", "siapa anda", "kamu siapa"
    ]

    first_word = q_clean.split()[0] if q_clean.split() else ""
    if first_word in greeting_words or any(bp in q_clean for bp in bot_profile_queries):
        return "greeting"

    # ==========================================
    # 2. INTENT: CLARIFICATION (PERTANYAAN TIDAK LENGKAP)
    # ==========================================
    words = q.split()
    
    # Kondisi A: Jika teks terlalu pendek (hanya 1 kata atau kosong)
    if len(words) <= 1:
        return "clarification"

    # Kondisi B: Keyword khusus yang memang menandakan kebingungan user
    ambiguous_keywords = [
        "tolong jelasin", "maksudnya gimana", "bisa bantu ga", "bingung nih"
    ]
    if any(keyword in q for keyword in ambiguous_keywords):
        return "clarification"

    # Kondisi C: KUNCI UTAMA UNTUK PERTANYAAN MENGGANTUNG
    # Jika user menanyakan topik spesifik instrumen, tetapi JENIS SEKOLAH/PERPUSTAKAANNYA tidak terdeteksi
    specific_instrument_keywords = [
        "kualifikasi kepala", "apa syarat kepala", "apa bukti fisik", "bagaimana akreditasi",
        "bagaimana penilaian", "komponen penilaian", "standar koleksi", "apa standar"
    ]
    
    if any(keyword in q for keyword in specific_instrument_keywords):
        # Jalankan deteksi library type yang sudah kita buat di layanan sebelumnya
        library_type = detect_library_type_question(question)
        
        # Jika tipe perpustakaannya tidak ketemu (UNKNOWN), berarti pertanyaannya tidak lengkap!
        if library_type == "UNKNOWN":
            return "clarification"

    # ==========================================
    # 3. INTENT: KNOWLEDGE (BISA DIPROSES RAG)
    # ==========================================
    return "knowledge"