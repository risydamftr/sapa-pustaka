import "./App.css";
import { useState, useEffect } from "react"; // Tambahkan useState dan useEffect
import Login from "./components/Login";
import ChatbotPage from "./pages/ChatbotPage";

function App() {
  // 1. Buat state dinamis untuk mengecek status login
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // 2. Cek apakah ada user_id di localStorage saat aplikasi pertama kali dimuat
    const userId = localStorage.getItem("user_id");
    if (userId) {
      setIsLoggedIn(true);
    } else {
      setIsLoggedIn(false);
    }
  }, []); // Berjalan sekali saat aplikasi di-refresh

  return (
    <>
      {
        isLoggedIn
          ? <ChatbotPage />
          : <Login />
      }
    </>
  );
}

export default App;