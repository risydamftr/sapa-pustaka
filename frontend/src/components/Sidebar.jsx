import { useState } from "react"; // Tambahkan useState untuk kontrol modal
import { useNavigate } from "react-router-dom";
import logo from "../assets/Icon headset.svg";
import newChat from "../assets/Icon new chat.svg";
import search from "../assets/Icon search.svg";
import settings from "../assets/icon configuration.svg";

function Sidebar() {
  const navigate = useNavigate();

  // State untuk mengontrol buka/tutup modal pengaturan
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Ambil data username secara dinamis dari localStorage
  const username = localStorage.getItem("user_name") || "Tamu";
  
  // Ambil huruf pertama username untuk dijadikan Avatar (Capitalized)
  const avatarInitial = username.charAt(0).toUpperCase();

  // Fungsi untuk Logout
  const handleLogout = () => {
    const confirmLogout = window.confirm("Apakah Anda yakin ingin keluar?");
    if (confirmLogout) {
      localStorage.clear(); // Hapus sesi login di browser
      navigate("/");        // Alihkan kembali ke halaman Login
    }
  };

  return (
    <div className="sidebar">

      {/* BAGIAN ATAS SIDEBAR */}
      <div>
        <div className="sidebar-logo">
          <img src={logo} alt="logo" />
        </div>

        {/* ========================================================= */}
        {/* TOMBOL PERCAKAPAN BARU (Sudah ditambahkan Custom Event) */}
        {/* ========================================================= */}
        <div 
          className="menu-item" 
          onClick={() => {
            window.dispatchEvent(new Event("resetChatEvent"));
          }} 
          style={{ cursor: 'pointer' }}
        >
          <img src={newChat} alt="" />
          <span>Percakapan Baru</span>
        </div>
        {/* ========================================================= */}

        <div className="menu-item">
          <img src={search} alt="" />
          <span>Cari Percakapan</span>
        </div>
      </div>

      {/* BAGIAN BAWAH SIDEBAR */}
      <div>
        {/* Menu Pengaturan - Ditambahkan onClick untuk membuka modal */}
        <div className="menu-item" onClick={() => setIsModalOpen(true)} style={{ cursor: 'pointer' }}>
          <img src={settings} alt="" />
          <span>Pengaturan</span>
        </div>

        {/* TOMBOL LOGOUT */}
        <div className="menu-item" onClick={handleLogout} style={{ cursor: 'pointer' }}>
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="20" 
            height="20" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="#ff4d4d" 
            strokeWidth="2.5" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
            <line x1="12" y1="2" x2="12" y2="12" />
          </svg>
          <span style={{ fontWeight: '500' }}>Logout</span>
        </div>

        {/* Profil Pengguna Dinamis */}
        <div className="user-card">
          <div className="avatar">
            {avatarInitial} 
          </div>

          <div>
            <div className="username">
              {username} 
            </div>
            <div className="role">
              Pengguna
            </div>
          </div>
        </div>

      </div>

      {/* ========================================================= */}
      {/* MODAL POP-UP PENGATURAN (Hanya muncul jika isModalOpen = true) */}
      {/* ========================================================= */}
      {isModalOpen && (
        <div className="settings-modal-overlay">
          <div className="settings-modal-content">
            <h3>Pengaturan Akun</h3>
            <div className="settings-body">
              <label>Nama Pengguna:</label>
              <input type="text" value={username} disabled />
              
              <label>Status Sistem:</label>
              <p>Berjalan di Server Lokal (Development)</p>
            </div>
            <button className="close-modal-btn" onClick={() => setIsModalOpen(false)}>
              Tutup
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

export default Sidebar;