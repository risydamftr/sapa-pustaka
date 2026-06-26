import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // Digunakan untuk memproteksi halaman jika belum login
import { askQuestion } from "../services/api";

function Chat() {
  const navigate = useNavigate();

  // 1. Ambil data login dari localStorage secara dinamis
  const username = localStorage.getItem("user_name") || "Tamu";
  const userId = localStorage.getItem("user_id");
  const sessionId = localStorage.getItem("session_id");

  // 2. Proteksi Halaman: Jika data login tidak ada, paksa user kembali ke halaman login (/)
  useEffect(() => {
    if (!userId) {
      navigate("/"); 
    }
  }, [userId, navigate]);

  const [question, setQuestion] = useState("");

  // Template pesan selamat datang dasar
  const welcomeMessage = {
    type: "welcome",
    title: `Halo, ${username}👋`,
    text: `Saya Sahabat Asistensi dan Pendampingan Perpustakaan yang siap membantu.\nSilahkan ajukan pertanyaan.`,
  };

  // Menggunakan nama dinamis dari localStorage untuk pesan selamat datang
  const [messages, setMessages] = useState([welcomeMessage]);
  const [loading, setLoading] = useState(false);
  
  // Fungsi untuk membersihkan obrolan (Dipicu ketika tombol Percakapan Baru di Sidebar diklik)
  const handleCreateNewChat = () => {
    setMessages([welcomeMessage]); // Kembalikan ke pesan selamat datang saja
    setQuestion(""); // Kosongkan input bar jika ada teks tertinggal
  };

  // =========================================================
  // EKSPOS FUNGSI KE WINDOW OBJECT DAN MENANGKAP CUSTOM EVENT
  // =========================================================
  useEffect(() => {
    // 1. Sinkronisasi via Pemanggilan Fungsi Window Langsung
    window.handleCreateNewChat = handleCreateNewChat;

    // 2. Sinkronisasi via Custom Event Listener (Double Protection)
    const handleResetSignal = () => {
      handleCreateNewChat();
    };
    window.addEventListener("resetChatEvent", handleResetSignal);
    
    // Bersihkan dari memori saat komponen dilepas
    return () => {
      delete window.handleCreateNewChat;
      window.removeEventListener("resetChatEvent", handleResetSignal);
    };
  }, [messages]); 
  // =========================================================

  async function handleSend() {
    if (!question.trim()) return;

    const currentQuestion = question;

    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: currentQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      // 3. Kirim pertanyaan beserta data pengirim (ID, Nama, Sesi) ke fungsi API
      const response = await askQuestion(
        currentQuestion,
        userId,
        username,
        sessionId
      );

      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Maaf, terjadi kesalahan.",
        },
      ]);
    }

    setLoading(false);
  }

  return (
    <div className="chat-main-container" style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", width: "100%" }}>
      
      <div className="chat-box" style={{ flex: 1, overflowY: "auto" }}>
        {messages.map((msg, index) => {
          if (msg.type === "welcome") {
            return (
              <div
                key={index}
                className="welcome-message"
              >
                <h2 className="welcome-title">
                  {msg.title}
                </h2>

                <p
                  className="welcome-text"
                  style={{
                    whiteSpace: "pre-line",
                  }}
                >
                  {msg.text}
                </p>
              </div>
            );
          }
          return (
            <div
              key={index}
              className={`message-row ${msg.type}`}
            >
              <div
                className={`message-bubble ${msg.type}`}
              >
                <div className="sender">
                  {msg.type === "user"
                    ? username
                    : "SAPA PUSTAKA"}
                </div>

                <p 
                  style={{
                    whiteSpace: "pre-line",
                  }}
                >
                  {msg.text}
                </p>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <b>Referensi:</b>
                    <ul>
                      {msg.sources.map((src, i) => (
                        <li key={i}>
                          📄 {src.source}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="message-row bot">
            <div className="message-bubble bot">
              <div className="sender">
                SAPA PUSTAKA
              </div>

              <p>
                Sedang mencari jawaban...
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="input-area">
        <input
          value={question}
          placeholder="Tulis pertanyaan..."
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSend();
            }
          }}
        />

        <button onClick={handleSend}>
          Kirim
        </button>
      </div>

    </div>
  );
}

export default Chat;