import Chat from "../components/chat";
import Sidebar from "../components/Sidebar";

function ChatbotPage() { // Mengubah nama fungsi menjadi sesuai nama file agar rapi
  return (
    /* PERBAIKAN UTAMA: Mengubah kelas menjadi app-container agar CSS pengunci layar aktif */
    <div className="app-container">

      <Sidebar />

      <main className="main-content">

        <div className="main-header">
          
          <h1>
            <span className="title-dark">
              SAPA
            </span>

            {" "}

            <span className="title-teal">
              PUSTAKA
            </span>
          </h1>

          <p className="tagline">
            Cepat Merespons, Hangat Mendampingi
          </p>

        </div>

        <Chat />

      </main>

    </div>
  );
}

export default ChatbotPage;