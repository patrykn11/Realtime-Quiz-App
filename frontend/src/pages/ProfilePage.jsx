import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../components/LoginContext";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useNavigate } from "react-router-dom";

import MyQuizzes from "../components/MyQuizzes";

export default function ProfilePage() {
  const { token, apiFetch } = useContext(AuthContext);
  const [stats, setStats] = useState([]);
  const [chartData, setChartData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resStats = await apiFetch("/api/user_stats/");
        const dataStats = await resStats.json();
        setStats(dataStats);
        const resChart = await apiFetch("/api/user_stats_per_day/");
        const dataChart = await resChart.json();
        setChartData(dataChart);
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };
    if (token) fetchData();
  }, [token, apiFetch]);


  return (
    <div className="flex flex-col items-center p-10 gap-10 w-full">
      <MyQuizzes />

      <h1 className="text-4xl font-bold text-white shadow-sm">
        Your statistics
      </h1>

      <div className="w-full max-w-4xl bg-white p-6 rounded-2xl shadow-2xl">
        <h2 className="text-[#7A1E31] font-bold text-sm">
          Daily Activity
        </h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis 
                dataKey="date" 
                tick={{fontSize: 11, fill: '#666'}} 
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                tick={{fontSize: 11, fill: '#666'}} 
                axisLine={false}
                tickLine={false}
                allowDecimals={false}
              />
              <Tooltip cursor={{fill: '#f9f9f9'}} />

              <Bar 
                dataKey="quizzes_played" 
                fill="#7A1E31" 
                barSize={15} 
                radius={[4, 4, 0, 0]} 
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="w-full max-w-4xl overflow-hidden rounded-2xl shadow-2xl bg-white">
        <table className="w-full text-left border-separate">
          <thead>
            <tr className="bg-[#7A1E31] text-white">
              <th className="px-6 py-4 font-bold uppercase text-xs first:rounded-tl-2xl">Quiz Name</th>
              <th className="px-6 py-4 font-bold uppercase text-xs text-center">Score</th>
              <th className="px-6 py-4 font-bold uppercase text-xs text-right last:rounded-tr-2xl">Date</th>
            </tr>
          </thead>
          <tbody className="text-black">
            {stats.length > 0 ? (
              stats.map((item, i) => (
                <tr
                  key={item.id ?? i}
                  onClick={() => item.game_id && navigate(`/profile/history/${item.game_id}`)}
                  className="border-b border-gray-100 even:bg-[#F8F9FA] cursor-pointer hover:bg-[#F4E8EC] transition-colors"
                >
                  <td className="px-6 py-4 font-medium text-gray-700">{item.quiz_name}</td>
                  <td className="px-6 py-4 text-center font-bold text-[#7A1E31]">{item.score} pts</td>
                  <td className="px-6 py-4 text-right text-sm text-gray-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            ) : (<></>)}
          </tbody>
        </table>
      </div>

    </div>
  );
}
