import "./App.css";

import Login from "./components/Login";
import ChatbotPage from "./pages/ChatbotPage";

function App() {

  const isLoggedIn = true;

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