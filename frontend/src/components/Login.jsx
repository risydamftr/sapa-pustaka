import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Digunakan untuk pindah ke halaman chat
import logo from "../assets/logologin.png";

function Login() {
  // 1. Definisikan State untuk menampung input dari user
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  // 2. Fungsi untuk menangani proses login saat tombol diklik atau form di-submit
  const handleLogin = (e) => {
    e.preventDefault(); // Mencegah page reload bawaan form HTML

    // Validasi sederhana agar input tidak kosong
    if (!username.trim() || !email.trim()) {
      alert("Harap isi Username dan Email terlebih dahulu!");
      return;
    }

    // Simpan data login ke localStorage browser agar bisa diakses oleh halaman chat
    localStorage.setItem("user_id", email);      // Email dipakai sebagai ID unik di DB
    localStorage.setItem("user_name", username);  // Username dipakai sebagai nama di DB
    
    // Membuat Session ID unik acak untuk sesi chat saat ini
    const randomSession = "SESS-" + Math.random().toString(36).substring(2, 11).toUpperCase();
    localStorage.setItem("session_id", randomSession);

    // 3. Pindahkan user ke halaman chat utama kamu
    // Ganti "/chat" di bawah ini sesuai dengan path route chatbot-mu di App.jsx
    window.location.href = "/"; 
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <img
          src={logo}
          alt="SAPA PUSTAKA"
          className="login-logo"
        />

        <p>Silakan masuk ke akun Anda</p>

        {/* Membungkus input dengan tag form agar support fitur submit 'Enter' */}
        <form onSubmit={handleLogin} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 'inherit' }}>
          
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="email" // Mengubah type menjadi email untuk validasi format standar browser
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <button type="submit" className="login-button">
            Login
          </button>
          
        </form>
      </div>
    </div>
  );
}

export default Login;