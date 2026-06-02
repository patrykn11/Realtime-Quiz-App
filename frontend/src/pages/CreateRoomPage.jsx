import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AuthContext } from "../components/LoginContext";
import { API_URL } from "../config";

export default function CreateRoomPage() {
  const { apiFetch } = useContext(AuthContext);
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuizId, setSelectedQuizId] = useState(null);
  const [error, setError] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        const response = await fetch(`${API_URL}/api/quizzes/`);
        if (!response.ok) throw new Error("Could not load quizzes.");
        setQuizzes(await response.json());
      } catch (requestError) {
        setError(requestError.message);
      }
    };

    fetchQuizzes();
  }, []);

  const createRoom = async () => {
    if (!selectedQuizId) {
      setError("Choose a quiz first.");
      return;
    }

    setError("");
    setIsCreating(true);
    try {
      const response = await apiFetch("/api/create_room/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz_id: selectedQuizId }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.quiz_id?.[0] || data.detail || "Could not create room.");
      }
      navigate(`/lobby/${data.room_code}`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsCreating(false);
    }
  };

  const selectedQuiz = quizzes.find((quiz) => quiz.id === selectedQuizId);

  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center gap-10">
      <div className="text-4xl font-semibold text-white">
        Choose your quiz and create room
      </div>

      <div className="flex flex-wrap justify-center gap-6 px-10">
        {quizzes.map((quiz) => (
          <button
            key={quiz.id}
            className={`rounded-2xl px-6 py-3 text-white shadow-md hover:shadow-lg ${
              selectedQuizId === quiz.id ? "bg-red-700" : "hover:bg-red-700"
            }`}
            onClick={() => setSelectedQuizId(quiz.id)}
          >
            {quiz.name}
          </button>
        ))}
      </div>

      <button
        className="rounded-2xl bg-orange-700 px-8 py-4 font-mono text-lg text-white shadow-lg hover:bg-orange-600 disabled:opacity-50"
        disabled={!selectedQuizId || isCreating}
        onClick={createRoom}
      >
        Create {selectedQuiz ? `'${selectedQuiz.name}'` : "quiz"} room
      </button>

      {error && <p className="text-red-200">{error}</p>}
    </div>
  );
}
