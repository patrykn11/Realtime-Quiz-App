import { useEffect, useState, useContext, useRef } from "react";
import { AuthContext } from "../components/LoginContext";
import { useParams, useNavigate } from "react-router-dom";
import Question from "../components/Question";

export default function QuizPage() {
  const { room_code } = useParams();
  const [question, setQuestion] = useState("");
  const [answers, setAnswers] = useState([]);
  const [timeLeft, setTimeLeft] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [scores, setScores] = useState([]); 
  const [myScore, setMyScore] = useState(null); 
  const [isFinished, setIsFinished] = useState(false);
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();
  const socketRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    let isEffectActive = true;
    const socket = new WebSocket(`ws://localhost:8000/ws/game/${room_code}/?token=${token}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "question" && isEffectActive) {
        setQuestion(data.question);
        setAnswers(data.answers);
        setSelectedAnswer(null);
        setIsFinished(false);

        const initialTime = data.time_limit;
        setTimeLeft(initialTime);

        if (timerRef.current) clearInterval(timerRef.current);

        timerRef.current = setInterval(() => {
          setTimeLeft((prev) => {
            if (prev <= 1) {
              clearInterval(timerRef.current);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      }

      if (data.type === "final_results" && isEffectActive) {
        setScores(data.ranking);
        setMyScore(data.own_score);
        setIsFinished(true); 
      }

      if (data.type === "game_over") {
        setIsFinished(true);
        setQuestion(""); 
        if (timerRef.current) clearInterval(timerRef.current);
      }
    };

    socket.onclose = () => {
      if (isEffectActive) navigate("/PinPage");
    };

    return () => {
      isEffectActive = false;
      socket.close();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [room_code, token, navigate]);

  const sendAnswer = (index) => {
    if (socketRef.current?.readyState === WebSocket.OPEN && timeLeft > 0) {
      setSelectedAnswer(index);
      socketRef.current.send(JSON.stringify({ type: "answer", answer: index }));
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-4">
      <h1 className="text-white text-3xl font-bold mb-6 tracking-wide uppercase">
        Room {room_code}
      </h1>

      {question ? (
        <Question
          question={question}
          answers={answers}
          onAnswer={sendAnswer}
          timeLeft={timeLeft}
          selectedAnswer={selectedAnswer}
        />
      ) : isFinished || scores.length > 0 || myScore !== null ? (
        <div className="bg-white w-full max-w-6xl rounded-xl p-8 md:p-12 shadow-2xl text-black flex flex-col items-center">
          
          <h2 className="text-4xl md:text-6xl font-black text-center mb-8 ">
            Your score: <span >{myScore ?? 0} points</span>
          </h2>
          
          <div className="h-px w-full bg-gray-200 my-8" />

          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-gray-400 text-center">
            Podium
          </h2>

          <div className="w-full max-w-2xl space-y-2">
            {scores
              .sort((a, b) => b.score - a.score)
              .map((s, idx) => (
                <div 
                  key={idx} 
                  className="flex justify-between items-center py-4 px-6 border-b border-gray-100"
                >
                  <span className="text-2xl font-bold text-gray-800">
                    {idx + 1}. {s.username}
                  </span>
                  <span className="text-2xl font-black">
                    {s.score} points
                  </span>
                </div>
              ))}
          </div>

        </div>
      ) : (
        <p className="text-white animate-pulse">Reconnect</p>
      )}
    </div>
  );
}