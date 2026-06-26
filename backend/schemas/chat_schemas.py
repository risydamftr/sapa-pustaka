from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    
    # Menambahkan field data pengguna sebagai opsional (Optional)
    # lengkap dengan nilai default agar sistem tidak crash jika ada request kosong
    user_id: Optional[str] = "UNKNOWN_USER"
    name: Optional[str] = "Tamu"
    session_id: Optional[str] = "DEFAULT_SESSION"