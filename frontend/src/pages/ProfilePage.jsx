import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../components/LoginContext";
import { API_URL } from "../config";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function ProfilePage() {
  const { token } = useContext(AuthContext);
  const [stats, setStats] = useState([]);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
      try {
        const resStats = await fetch(`${API_URL}/api/user_stats/`, { headers });
        const dataStats = await resStats.json();
        setStats(dataStats);
        const resChart = await fetch(`${API_URL}/api/user_stats_per_day/`, { headers });
        const dataChart = await resChart.json();
        setChartData(dataChart);
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };
    if (token) fetchData();
  }, [token]);


  return (
    <div className="flex flex-col items-center p-10 gap-10 w-full">
      
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
                <tr key={i} className="border-b border-gray-100 even:bg-[#F8F9FA]">
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