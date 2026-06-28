# SAPA PUSTAKA (Sistem Asistensi & Pendampingan Akreditasi Pustaka)

Aplikasi asisten berbasis AI terintegrasi untuk membantu standarisasi dan persiapan dokumen akreditasi perpustakaan sekolah di Indonesia.

## 🛠️ Struktur Proyek
- **backend/** : Menyediakan API layanan, manajemen sesi pengguna, sinkronisasi basis data akreditasi, dan integrasi modul AI.
- **frontend/** : Antarmuka chat interaktif berbasis React + Vite yang mendukung rendering Markdown otomatis via `react-markdown`.

## 🚀 Panduan Memulai (Getting Started)

### Prasyarat
- Node.js (Versi LTS terbaru)
- Python 3.x (untuk lingkungan virtual backend jika diperlukan)

### Langkah Instalasi Frontend
1. Masuk ke direktori frontend:
   cd frontend
2. Instal semua dependensi yang diperlukan:
   npm install
3. Jalankan server lokal untuk pengembangan:
   npm run dev

### Langkah Instalasi Backend
1. Masuk ke direktori backend:
   cd backend
2. Instal dependensi sesuai dengan manajemen paket yang Anda gunakan (misalnya menggunakan pip jika berbasis Python):
   pip install -r requirements.txt
3. Jalankan server backend Anda.
   venv\Scripts\activate
   uvicorn app:app --reload
