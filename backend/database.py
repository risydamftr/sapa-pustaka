import os
import uuid  # Tambahan untuk generate ID acak otomatis
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# 1. Tentukan lokasi file sapa_pustaka.db (otomatis dibuat di folder yang sama)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sapa_pustaka.db')}"

# 2. Atur Koneksi Engine & Session SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================================================
# DEFINISI MODEL TABEL (Hanya Pengguna & Chat)
# ==================================================

class User(Base):
    __tablename__ = "users"

    # user_id sekarang otomatis digenerate berupa string UUID unik jika tidak diisi manual
    user_id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))  
    name = Column(String(100), nullable=True)       # Nama Pengguna (opsional)
    library_type = Column(String(20), default="UNKNOWN")  # SD, SMP, SMA
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Hubungan relasi ke tabel chat_history
    chats = relationship("ChatHistory", back_populates="user")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # UBAH NULLABLE MENJADI TRUE AGAR TIDAK ERROR JIKA KOSONG
    session_id = Column(String(100), nullable=True) 
    
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=True)
    role = Column(String(10), nullable=False)        # 'user' atau 'assistant'
    message = Column(Text, nullable=False)           # Isi pesan teks
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")

# ==================================================
# FUNGSI MEMBUAT FILE DATABASE
# ==================================================
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✨ File 'sapa_pustaka.db' dengan tabel Pengguna & Chat History berhasil dibuat!")

if __name__ == "__main__":
    init_db()