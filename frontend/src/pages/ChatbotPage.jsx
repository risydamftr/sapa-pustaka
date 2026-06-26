import Chat from "../components/chat";
import Sidebar from "../components/Sidebar";

function App() {
  return (
    <div className="app-layout">

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

export default App;