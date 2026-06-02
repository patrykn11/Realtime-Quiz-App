import { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AuthContext } from "../components/LoginContext";

export default function QuizHistoryRankingPage() {
  const { gameId } = useParams();
  const { token, apiFetch } = useContext(AuthContext);
  const navigate = useNavigate();
  const [rankingData, setRankingData] = useState(null);

  useEffect(() => {
    const fetchRanking = async () => {
      try {
        const response = await apiFetch(`/api/quiz_history/${gameId}/ranking/`);
        if (!response.ok) {
          navigate("/profile");
          return;
        }
        

        const data = await response.json();
        setRankingData(data);
      } catch (err) {
        console.error("Fetch error:", err);
        navigate("/profile");
      }
    };

    if (token) fetchRanking();
  }, [apiFetch, gameId, navigate, token]);

  const scores = rankingData?.ranking ?? [];

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-4">
      {rankingData ? (
        <div className="bg-white w-full max-w-6xl rounded-xl p-8 md:p-12 shadow-2xl text-black flex flex-col items-center">
          <p className="text-sm font-bold uppercase tracking-wide text-gray-400 mb-3">
            {rankingData.quiz_name} · {new Date(rankingData.date).toLocaleDateString()}
          </p>
          <h2 className="text-4xl md:text-6xl font-black text-center mb-8">
            Your score: <span>{rankingData.own_score ?? 0} points</span>
          </h2>
          <div className="h-px w-full bg-gray-200 my-8" />
          <h2 className="text-2xl md:text-3xl font-bold mb-8 text-gray-400 text-center">Podium</h2>
          <div className="w-full max-w-2xl space-y-2">
            {scores.map((score, idx) => (

              <div key={`${score.username}-${idx}`} className="flex justify-between items-center py-4 px-6 border-b ">
                <span className="text-2xl font-bold text-gray-800">{idx + 1}. {score.username}</span>
                <span className="text-2xl font-black">{score.score} points</span>
              </div>
            ))}
          </div>
        </div>
      ) : <></>}
    </div>
  );
}
