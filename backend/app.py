from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin, ModelView

from schemas.chat_schemas import ChatRequest
from services.chat_services import answer_question

# Hubungkan dengan database.py yang baru dibuat
from database import engine, User, ChatHistory, SessionLocal, Base

app = FastAPI()

# 2. AUTO-CREATE TABEL: Tambahkan perintah ini agar tabel otomatis dibuat saat aplikasi jalan
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# CONFIGURATION SQLADMIN (Hanya Pengguna & Chat)
# ==================================================
admin = Admin(app, engine, session_maker=SessionLocal)

# Tampilan Panel Pengguna
class UserAdmin(ModelView, model=User):
    column_list = [User.user_id, User.name, User.library_type, User.created_at]
    name = "Pengguna"
    name_plural = "Daftar Pengguna"
    icon = "fa-solid fa-user"

# Tampilan Panel Riwayat Chat
class ChatHistoryAdmin(ModelView, model=ChatHistory):
    column_list = [ChatHistory.chat_id, ChatHistory.session_id, ChatHistory.role, ChatHistory.message, ChatHistory.timestamp]
    searchable_columns = [ChatHistory.message, ChatHistory.session_id]
    name = "Riwayat Chat"
    name_plural = "Riwayat Chat"
    icon = "fa-solid fa-comment"

# Daftarkan kedua panel ke dashboard web
admin.add_view(UserAdmin)
admin.add_view(ChatHistoryAdmin)


# ==================================================
# ENDPOINTS
# ==================================================
@app.get("/")
def root():
    return {
        "message": "Chatbot AI Running"
    }

@app.post("/chat")
def chat(data: ChatRequest):
    # Mengambil properti tambahan dari data frontend, jika tidak dikirim akan menggunakan nilai default
    user_id = getattr(data, 'user_id', 'UNKNOWN_USER')
    name = getattr(data, 'name', 'Tamu')
    session_id = getattr(data, 'session_id', 'DEFAULT_SESSION')

    # Meneruskan semua parameter data pengguna ke logika chat_services
    return answer_question(
        question=data.question,
        user_id=user_id,
        name=name,
        session_id=session_id
    )