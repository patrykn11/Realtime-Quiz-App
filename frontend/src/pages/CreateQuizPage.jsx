import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AuthContext } from "../components/LoginContext";
import QuizQuestionForm from "../components/QuizQuestionForm";

let nextFieldId = 0;

const createFieldId = (prefix) => {
  nextFieldId += 1;
  return `${prefix}-${nextFieldId}`;
};

const createChoice = () => ({
  id: createFieldId("choice"),
  text: "",
});

const createQuestion = () => {
  const firstChoice = createChoice();

  return {
    id: createFieldId("question"),
    text: "",
    choices: [firstChoice, createChoice()],
    correctChoiceId: firstChoice.id,
  };
};

const findFirstError = (value) => {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    for (const item of value) {
      const error = findFirstError(item);
      if (error) return error;
    }
  }
  if (value && typeof value === "object") {
    for (const item of Object.values(value)) {
      const error = findFirstError(item);
      if (error) return error;
    }
  }
  return "";
};

const inputClass =
  "w-full rounded-xl border border-white/20 bg-white px-4 py-3 text-black outline-none focus:ring-2 focus:ring-orange-400";

export default function CreateQuizPage() {
  const { apiFetch, token } = useContext(AuthContext);
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [questions, setQuestions] = useState(() => [createQuestion()]);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateQuestionText = (questionId, text) => {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) =>
        question.id === questionId ? { ...question, text } : question,
      ),
    );
  };

  const updateChoiceText = (questionId, choiceId, text) => {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) =>
        question.id === questionId
          ? {
              ...question,
              choices: question.choices.map((choice) =>
                choice.id === choiceId ? { ...choice, text } : choice,
              ),
            }
          : question,
      ),
    );
  };

  const setCorrectChoice = (questionId, choiceId) => {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) =>
        question.id === questionId
          ? { ...question, correctChoiceId: choiceId }
          : question,
      ),
    );
  };

  const addChoice = (questionId) => {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) =>
        question.id === questionId
          ? { ...question, choices: [...question.choices, createChoice()] }
          : question,
      ),
    );
  };

  const removeChoice = (questionId, choiceId) => {
    setQuestions((currentQuestions) =>
      currentQuestions.map((question) => {
        if (question.id !== questionId || question.choices.length <= 2) {
          return question;
        }

        const choices = question.choices.filter((choice) => choice.id !== choiceId);
        return {
          ...question,
          choices,
          correctChoiceId:
            question.correctChoiceId === choiceId
              ? choices[0].id
              : question.correctChoiceId,
        };
      }),
    );
  };

  const removeQuestion = (questionId) => {
    setQuestions((currentQuestions) =>
      currentQuestions.length > 1
        ? currentQuestions.filter((question) => question.id !== questionId)
        : currentQuestions,
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!token) {
      navigate("/login");
      return;
    }

    const payload = {
      name: name.trim(),
      questions: questions.map((question) => ({
        text: question.text.trim(),
        choices: question.choices.map((choice) => ({
          text: choice.text.trim(),
          is_correct: choice.id === question.correctChoiceId,
        })),
      })),
    };

    if (!payload.name) {
      setError("Quiz name is required.");
      return;
    }

    if (payload.questions.some((question) => !question.text)) {
      setError("Every question needs text.");
      return;
    }

    if (
      payload.questions.some((question) =>
        question.choices.some((choice) => !choice.text),
      )
    ) {
      setError("Every answer needs text.");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await apiFetch("/api/create_quiz/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(findFirstError(data) || "Could not create quiz.");
      }

      navigate("/create-room");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-full px-4 py-10 text-white sm:px-8">
      <form className="mx-auto flex w-full max-w-4xl flex-col gap-8" onSubmit={handleSubmit}>
        <div>
          <h1 className="font-mono text-3xl font-semibold">CREATE QUIZ</h1>
          <p className="mt-2 text-white/75">
            Add questions, choose one correct answer and create your quiz.
          </p>
        </div>

        <label className="flex flex-col gap-2 font-mono">
          Quiz name
          <input
            className={inputClass}
            maxLength={32}
            placeholder="Quiz name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
        </label>

        <div className="flex flex-col gap-6">
          {questions.map((question, questionIndex) => (
            <QuizQuestionForm
              key={question.id}
              question={question}
              questionNumber={questionIndex + 1}
              canRemoveQuestion={questions.length > 1}
              onQuestionTextChange={updateQuestionText}
              onChoiceTextChange={updateChoiceText}
              onCorrectChoiceChange={setCorrectChoice}
              onAddChoice={addChoice}
              onRemoveChoice={removeChoice}
              onRemoveQuestion={removeQuestion}
            />
          ))}
        </div>

        <button
          type="button"
          className="self-start rounded-xl border border-white/40 px-5 py-3 font-mono hover:bg-white hover:text-black"
          onClick={() => setQuestions((currentQuestions) => [...currentQuestions, createQuestion()])}
        >
          + Add question
        </button>

        {error && (
          <p role="alert" className="rounded-xl bg-red-950/50 p-4 text-red-100">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-2xl bg-orange-700 px-8 py-4 font-mono text-lg shadow-lg hover:bg-orange-600 disabled:cursor-wait disabled:opacity-50"
        >
          {isSubmitting ? "Creating quiz..." : "Create quiz"}
        </button>
      </form>
    </div>
  );
}
