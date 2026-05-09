import React from "react";

export default function Question({ question, answers, onAnswer, timeLeft, selectedAnswer, questionResults }) {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const hasResults = Boolean(questionResults);

  const getAnswerClass = (index) => {
    if (!hasResults) {
      return selectedAnswer === index
        ? "bg-indigo-600 text-white border border-indigo-700 shadow-xl"
        : "bg-white text-gray-800 border border-gray-100 hover:shadow-lg hover:bg-gray-50";
    }

    if (questionResults.correct_answer === index) {
      return "bg-green-600 text-white border border-green-700 shadow-xl";
    }

    if (selectedAnswer === index) {
      return "bg-red-600 text-white border border-red-700 shadow-xl";
    }

    return "bg-white text-gray-400 border border-gray-100";
  };

  return (
    <div className="bg-white w-full max-w-6xl rounded-xl p-8 md:p-12 shadow-2xl text-black">
      
      <div className="flex items-center space-x-4 mb-8 text-sm font-semibold text-gray-500">
        <div className="bg-[#1e4620] text-[#4ade80] px-3 py-1 rounded text-xs font-mono">
          Time: {formatTime(timeLeft)}
        </div>
      </div>

      <h2 className="text-4xl md:text-6xl font-black text-center mb-12">
        {question}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {answers.map((ans, index) => {
          return (
            <button
              key={index}
              className={`w-full py-5 px-8 rounded-full text-2xl font-bold shadow-md transition-all
                ${getAnswerClass(index)}`}
              onClick={() => onAnswer(index)}
              disabled={hasResults}
            >
              {ans}
            </button>
          );
        })}
      </div>

      {hasResults ? (
        <div className="mt-10 border-t border-gray-200 pt-8">
          <h3 className="text-2xl font-black text-center mb-6">
            Correct answer: {answers[questionResults.correct_answer]}
          </h3>
          <div className="w-full max-w-2xl mx-auto space-y-2">
            {questionResults.results.map((result) => (
              <div
                key={result.username}
                className="flex justify-between items-center py-3 px-5 border-b border-gray-100"
              >
                <span className="text-xl font-bold text-gray-800">{result.username}</span>
                <span className={`text-lg font-black ${result.is_correct ? "text-green-600" : "text-red-600"}`}>
                  {result.is_correct ? "Correct" : "Wrong"}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : <></>}
    </div>
  );
}
