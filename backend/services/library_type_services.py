def detect_library_type_question(question):
    q = question.lower()
    words = q.replace("?", "").replace(",","").replace(".", "").split()

    # ==========================================
    # 1. CEK KATA KUNCI PANJANG & SPESIFIK DULU
    # ==========================================
    if "lembaga nonpemerintah" in q or "lembaga non pemerintah" in q:
        return "KHUSUS_NONPEMERINTAH"
        
    elif "lembaga pemerintah" in q:
        return "KHUSUS_PEMERINTAH"

    elif "rumah ibadah" in q:
        return "RUMAH_IBADAH"

    elif "perpustakaan provinsi" in q:
        return "PROVINSI"

    elif "perpustakaan kabupaten" in q or "perpustakaan kota" in q or "kab/kota" in q:
        return "KABUPATEN_KOTA"

    elif "perpustakaan kecamatan" in q:
        return "KECAMATAN"

    elif "perpustakaan desa" in q or "perpustakaan kelurahan" in q:
        return "DESA_KELURAHAN"

    elif "perpustakaan universitas" in q:
        return "UNIVERSITAS"

    elif "institut" in q or "sekolah tinggi" in q or "politeknik" in q:
        return "POLITEKNIK"

    elif "perpustakaan akademi" in q or "akademi komunitas" in q:
        return "AKADEMI_KOMUNITAS"

    # ==========================================
    # 2. CEK TINGKAT SEKOLAH (Paling Bawah & Berbasis Kata Utuh)
    # ==========================================
    elif "paud" in words or "tk" in words or "ra" in words or "tk - ra" in q:
        return "PAUD"

    elif "slb" in words:
        return "SLB"

    elif "smp" in words or "mts" in words:
        return "SMP"

    elif "sma" in words or "smk" in words or "ma" in words or "mak" in words:
        return "SMA"
        
    elif "sd" in words or "mi" in words:
        return "SD"

    return "UNKNOWN"