import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; 
import { askQuestion } from "../services/api";
// --- 1. IMPORT REACT MARKDOWN DI SINI ---
import ReactMarkdown from "react-markdown";

function Chat() {
  const navigate = useNavigate();

  const username = localStorage.getItem("user_name") || "Tamu";
  const userId = localStorage.getItem("user_id");
  const sessionId = localStorage.getItem("session_id");

  useEffect(() => {
    const currentUserId = localStorage.getItem("user_id");
    if (!currentUserId) {
      navigate("/"); 
    }
  }, [navigate]); 

  const [question, setQuestion] = useState("");

  const welcomeMessage = {
    type: "welcome",
    title: `Halo, ${username}👋`,
    text: `Saya Sahabat Asistensi dan Pendampingan Perpustakaan yang siap membantu.\nSilahkan ajukan pertanyaan.`,
  };

  const [messages, setMessages] = useState([welcomeMessage]);
  const [loading, setLoading] = useState(false);
  
  const handleCreateNewChat = () => {
    setMessages([welcomeMessage]); 
    setQuestion(""); 
  };

  useEffect(() => {
    const handleResetSignal = () => {
      handleCreateNewChat();
    };

    window.addEventListener("resetChatEvent", handleResetSignal);
    
    return () => {
      window.removeEventListener("resetChatEvent", handleResetSignal);
    };
  }, []);

  async function handleSend() {
    if (!question.trim() || loading) return;

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
      const response = await askQuestion(
        currentQuestion,
        userId,
        username,
        sessionId
      );

      const botReply = response?.answer || response?.reply || response?.message || "Sistem tidak memberikan teks jawaban.";

      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: botReply,
          sources: response?.sources || [],
        },
      ]);
    } catch (error) {
      console.error("Error saat memanggil API:", error);
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Maaf, terjadi kesalahan pada sistem.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-main-container" style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0, width: "100%" }}>
      
      <div className="chat-box" style={{ flex: 1, overflowY: "auto" }}>
        {messages.map((msg, index) => {
          if (msg.type === "welcome") {
            return (
              <div
                key={index}
                className="welcome-message"
              >
                <h2 className="welcome-title">
                  {msg?.title || "Selamat Datang"}
                </h2>

                <p
                  className="welcome-text"
                  style={{
                    whiteSpace: "pre-line",
                  }}
                >
                  {msg?.text || ""}
                </p>
              </div>
            );
          }
          return (
            <div
              key={index}
              className={`message-row ${msg?.type || "bot"}`}
            >
              <div
                className={`message-bubble ${msg?.type || "bot"}`}
              >
                <div className="sender">
                  {msg?.type === "user"
                    ? username
                    : "SAPA PUSTAKA"}
                </div>

                {/* --- 2. UBAH DARI TAG <p> BIASA MENJADI <ReactMarkdown> --- */}
                <div className="message-text-content">
                  <ReactMarkdown>
                    {msg?.text || "Tidak ada pesan teks yang diterima."}
                  </ReactMarkdown>
                </div>
                {msg?.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <b>Referensi:</b>
                    <ul>
                      {msg.sources.map((src, i) => (
                        <li key={i}>
                          📄 {src?.source || "Sumber tidak diketahui"}
                          </li> // <-- SEBELUMNYA TERTULIS </td>, GANTI JADI TENTU </li>
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
          placeholder={loading ? "Sedang memproses..." : "Tulis pertanyaan..."}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading} 
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSend();
            }
          }}
        />

        <button onClick={handleSend} disabled={loading}>
          {loading ? "..." : "Kirim"} 
        </button>
      </div>

    </div>
  );
}

export default Chat;