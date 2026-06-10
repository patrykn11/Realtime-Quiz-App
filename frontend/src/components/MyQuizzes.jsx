import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AuthContext } from "./LoginContext";

const readError = async (response) => {
  const data = await response.json().catch(() => ({}));
  return data.detail || "Could not complete the request.";
};

export default function MyQuizzes() {
  const { token, apiFetch } = useContext(AuthContext);
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [deletingQuizId, setDeletingQuizId] = useState(null);

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return undefined;
    }

    let isActive = true;

    const fetchQuizzes = async () => {
      setError("");
      setIsLoading(true);

      try {
        const response = await apiFetch("/api/my_quizzes/");
        if (!response.ok) {
          throw new Error(await readError(response));
        }

        const data = await response.json();
        if (isActive) setQuizzes(data);
      } catch (requestError) {
        if (isActive) setError(requestError.message);
      } finally {
        if (isActive) setIsLoading(false);
      }
    };

    fetchQuizzes();
    return () => {
      isActive = false;
    };
  }, [apiFetch, token]);

  const deleteQuiz = async (quiz) => {
    const confirmed = window.confirm(
      `Delete "${quiz.name}"? Its questions, answers and related game history will also be deleted.`,
    );
    if (!confirmed) return;

    setError("");
    setDeletingQuizId(quiz.id);

    try {
      const response = await apiFetch(`/api/quizzes/${quiz.id}/`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error(await readError(response));
      }

      setQuizzes((currentQuizzes) =>
        currentQuizzes.filter((currentQuiz) => currentQuiz.id !== quiz.id),
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setDeletingQuizId(null);
    }
  };

  return (
    <section className="w-full max-w-4xl rounded-2xl bg-white p-6 shadow-2xl">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-bold text-[#7A1E31]">My quizzes</h2>
        <button
          type="button"
          className="rounded-xl bg-[#7A1E31] px-4 py-2 font-mono text-white hover:bg-[#982943]"
          onClick={() => navigate("/create-quiz")}
        >
          + Create quiz
        </button>
      </div>

      {isLoading && <p className="text-gray-500">Loading quizzes...</p>}

      {!isLoading && quizzes.length === 0 && !error && (
        <p className="text-gray-500">You have not created any quizzes yet.</p>
      )}

      {quizzes.length > 0 && (
        <div className="flex flex-col gap-3">
          {quizzes.map((quiz) => (
            <article
              key={quiz.id}
              className="flex flex-col gap-3 rounded-xl border border-gray-200 p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <h3 className="font-semibold text-gray-800">{quiz.name}</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {quiz.question_count} {quiz.question_count === 1 ? "question" : "questions"}
                  {" · "}
                  {new Date(quiz.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={deletingQuizId === quiz.id}
                  className="rounded-xl border border-[#7A1E31] px-4 py-2 font-mono text-[#7A1E31] hover:bg-[#7A1E31] hover:text-white disabled:opacity-50"
                  onClick={() => navigate(`/quizzes/${quiz.id}/edit`)}
                >
                  Edit
                </button>
                <button
                  type="button"
                  disabled={deletingQuizId === quiz.id}
                  className="rounded-xl border border-red-700 px-4 py-2 font-mono text-red-700 hover:bg-red-700 hover:text-white disabled:cursor-wait disabled:opacity-50"
                  onClick={() => deleteQuiz(quiz)}
                >
                  {deletingQuizId === quiz.id ? "Deleting..." : "Delete"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {error && (
        <p role="alert" className="mt-4 rounded-xl bg-red-100 p-3 text-red-800">
          {error}
        </p>
      )}
    </section>
  );
}
