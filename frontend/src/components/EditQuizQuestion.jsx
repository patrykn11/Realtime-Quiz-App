import { useEffect, useState } from "react";

export default function EditQuizQuestion({
  question,
  questionNumber,
  onSave,
  onDelete,
}) {
  const [text, setText] = useState(question.text);
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    setText(question.text);
  }, [question.text]);

  const saveQuestion = async (event) => {
    event.preventDefault();
    const trimmedText = text.trim();

    if (!trimmedText) {
      setError("Question text is required.");
      return;
    }

    setError("");
    setIsSaving(true);
    try {
      await onSave(question.id, trimmedText);
      setText(trimmedText);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsSaving(false);
    }
  };

  const deleteQuestion = async () => {
    const confirmed = window.confirm(
      `Delete question ${questionNumber}? Its answers will also be deleted.`,
    );
    if (!confirmed) return;

    setError("");
    setIsDeleting(true);
    try {
      await onDelete(question.id);
    } catch (requestError) {
      setError(requestError.message);
      setIsDeleting(false);
    }
  };

  const isUnchanged = text.trim() === question.text;

  return (
    <form
      className="rounded-2xl border border-white/20 bg-black/15 p-5 shadow-xl sm:p-6"
      onSubmit={saveQuestion}
    >
      <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
        <h2 className="font-mono text-xl">Question {questionNumber}</h2>
        <button
          type="button"
          disabled={isSaving || isDeleting}
          className="rounded-xl border border-red-300 px-4 py-2 text-sm text-red-100 hover:bg-red-800 disabled:cursor-wait disabled:opacity-50"
          onClick={deleteQuestion}
        >
          {isDeleting ? "Deleting..." : "Delete question"}
        </button>
      </div>

      <label className="flex flex-col gap-2 font-mono">
        Question text
        <input
          className="w-full rounded-xl border border-white/20 bg-white px-4 py-3 text-black outline-none focus:ring-2 focus:ring-orange-400"
          maxLength={255}
          value={text}
          onChange={(event) => setText(event.target.value)}
          required
        />
      </label>

      <div className="mt-5">
        <h3 className="mb-2 text-sm font-semibold text-white/75">Answers</h3>
        <ul className="grid gap-2 sm:grid-cols-2">
          {question.choices.map((choice) => (
            <li
              key={choice.id}
              className={`flex items-center justify-between gap-3 rounded-xl px-4 py-3 ${
                choice.is_correct ? "bg-green-900/60" : "bg-white/10"
              }`}
            >
              <span>{choice.text}</span>
              {choice.is_correct && (
                <span className="rounded-lg bg-green-200 px-2 py-1 text-xs font-semibold text-green-900">
                  Correct
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-xl bg-red-950/50 p-3 text-red-100">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={isSaving || isDeleting || isUnchanged || !text.trim()}
        className="mt-5 rounded-xl bg-orange-700 px-5 py-3 font-mono hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {isSaving ? "Saving..." : "Save question"}
      </button>
    </form>
  );
}
