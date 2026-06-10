import { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import EditQuizQuestion from "../components/EditQuizQuestion";
import { AuthContext } from "../components/LoginContext";

const readError = async (response) => {
  const data = await response.json().catch(() => ({}));
  const firstError = Object.values(data).flat(Infinity)[0];
  return firstError || data.detail || "Could not complete the request.";
};

export default function EditQuizPage() {
  const { quizId } = useParams();
  const { token, apiFetch } = useContext(AuthContext);
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return undefined;
    }

    let isActive = true;

    const fetchQuiz = async () => {
      setError("");
      setIsLoading(true);

      try {
        const response = await apiFetch(`/api/quizzes/${quizId}/`);
        if (!response.ok) {
          throw new Error(await readError(response));
        }

        const data = await response.json();
        if (isActive) setQuiz(data);
      } catch (requestError) {
        if (isActive) setError(requestError.message);
      } finally {
        if (isActive) setIsLoading(false);
      }
    };

    fetchQuiz();
    return () => {
      isActive = false;
    };
  }, [apiFetch, quizId, token]);

  const updateQuestion = async (questionId, text) => {
    const response = await apiFetch(`/api/question/${questionId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    const updatedQuestion = await response.json();
    setQuiz((currentQuiz) => ({
      ...currentQuiz,
      questions: currentQuiz.questions.map((question) =>
        question.id === questionId
          ? { ...question, text: updatedQuestion.text }
          : question,
      ),
    }));
  };

  const deleteQuestion = async (questionId) => {
    const response = await apiFetch(`/api/question/${questionId}/`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(await readError(response));
    }

    setQuiz((currentQuiz) => ({
      ...currentQuiz,
      questions: currentQuiz.questions.filter(
        (question) => question.id !== questionId,
      ),
    }));
  };

  if (!token) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-white">
        <p>You need to sign in to edit a quiz.</p>
        <button
          type="button"
          className="rounded-xl border border-white px-5 py-2 font-mono hover:bg-white hover:text-black"
          onClick={() => navigate("/login")}
        >
          Sign in
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full px-4 py-10 text-white sm:px-8">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-mono text-3xl font-semibold">{quiz?.name || "Edit quiz"}</h1>
            <p className="mt-2 text-white/75">Change or delete quiz questions.</p>
          </div>
          <button
            type="button"
            className="rounded-xl border border-white/40 px-4 py-2 font-mono hover:bg-white hover:text-black"
            onClick={() => navigate("/profile")}
          >
            Back to profile
          </button>
        </div>

        {isLoading && <p>Loading quiz...</p>}

        {error && (
          <p role="alert" className="rounded-xl bg-red-950/50 p-4 text-red-100">
            {error}
          </p>
        )}

        {!isLoading && quiz?.questions.length === 0 && (
          <div className="rounded-2xl bg-black/15 p-6 text-white/75">
            This quiz has no questions.
          </div>
        )}

        {quiz?.questions.map((question, questionIndex) => (
          <EditQuizQuestion
            key={question.id}
            question={question}
            questionNumber={questionIndex + 1}
            onSave={updateQuestion}
            onDelete={deleteQuestion}
          />
        ))}
      </div>
    </div>
  );
}
