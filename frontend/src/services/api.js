const API_URL = "http://127.0.0.1:8000";

export async function askQuestion(question, userId, name, sessionId) {
  const response = await fetch(
    `${API_URL}/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: question,
        user_id: userId,       // Dikirim ke backend sebagai user_id
        name: name,            // Dikirim ke backend sebagai name
        session_id: sessionId   // Dikirim ke backend sebagai session_id
      })
    }
  );

  if (!response.ok) {
    throw new Error("Gagal menghubungi server");
  }

  return await response.json();
}