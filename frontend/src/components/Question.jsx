import React from "react";

export default function Question({ question, answers, onAnswer, timeLeft, selectedAnswer }) {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white w-full max-w-6xl rounded-xl p-8 md:p-12 shadow-2xl text-black">
      
      <div className="flex items-center space-x-4 mb-8 text-sm font-semibold text-gray-500">
        <div className="bg-[#1e4620] text-[#4ade80] px-3 py-1 rounded text-xs font-mono">
          Time: {formatTime(timeLeft)}
        </div>
      </div>

      <h2 className="text-4xl md:text-6xl font-black text-center mb-12 tracking-tight">
        {question}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {answers.map((ans, index) => {
          const isSelected = selectedAnswer === index;
          return (
            <button
              key={index}
              className={`w-full py-5 px-8 rounded-full text-2xl font-bold shadow-md transition-all
                ${isSelected 
                  ? "bg-indigo-600 text-white border border-indigo-700 shadow-xl scale-[1.02]" 
                  : "bg-white text-gray-800 border border-gray-100 hover:shadow-lg hover:bg-gray-50"
                }`}
              onClick={() => onAnswer(index)}
            >
              {ans}
            </button>
          );
        })}
      </div>
    </div>
  );
}