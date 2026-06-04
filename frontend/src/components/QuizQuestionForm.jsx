const inputClass =
  "w-full rounded-xl border border-white/20 bg-white px-4 py-3 text-black outline-none focus:ring-2 focus:ring-orange-400";

export default function QuizQuestionForm({
  question,
  questionNumber,
  canRemoveQuestion,
  onQuestionTextChange,
  onChoiceTextChange,
  onCorrectChoiceChange,
  onAddChoice,
  onRemoveChoice,
  onRemoveQuestion,
}) {
  return (
    <section className="rounded-2xl border border-white/20 bg-black/15 p-5 shadow-xl sm:p-6">
      <div className="mb-5 flex items-center justify-between gap-4">
        <h2 className="font-mono text-xl">Question {questionNumber}</h2>
        <button
          type="button"
          className="rounded-lg px-3 py-2 text-sm hover:bg-red-800 disabled:cursor-not-allowed disabled:opacity-40"
          disabled={!canRemoveQuestion}
          onClick={() => onRemoveQuestion(question.id)}
        >
          Remove question
        </button>
      </div>

      <input
        className={inputClass}
        maxLength={255}
        placeholder="Question text"
        value={question.text}
        onChange={(event) => onQuestionTextChange(question.id, event.target.value)}
        required
      />

      <div className="mt-5 flex flex-col gap-3">
        {question.choices.map((choice, choiceIndex) => (
          <div
            key={choice.id}
            className="grid gap-3 rounded-xl bg-white/10 p-3 sm:grid-cols-[auto_1fr_auto] sm:items-center"
          >
            <label className="flex cursor-pointer items-center gap-2 text-sm">
              <input
                type="radio"
                name={`correct-${question.id}`}
                checked={question.correctChoiceId === choice.id}
                onChange={() => onCorrectChoiceChange(question.id, choice.id)}
              />
              Correct
            </label>
            <input
              className={inputClass}
              maxLength={255}
              placeholder={`Answer ${choiceIndex + 1}`}
              value={choice.text}
              onChange={(event) =>
                onChoiceTextChange(question.id, choice.id, event.target.value)
              }
              required
            />
            <button
              type="button"
              className="rounded-lg px-3 py-2 text-sm hover:bg-red-800 disabled:cursor-not-allowed disabled:opacity-40"
              disabled={question.choices.length === 2}
              onClick={() => onRemoveChoice(question.id, choice.id)}
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      <button
        type="button"
        className="mt-4 rounded-xl border border-white/30 px-4 py-2 font-mono hover:bg-white hover:text-black"
        onClick={() => onAddChoice(question.id)}
      >
        + Add answer
      </button>
    </section>
  );
}
