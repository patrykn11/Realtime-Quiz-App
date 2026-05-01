
import { useContext, useState, useEffect } from "react";
import { AuthContext } from "../components/LoginContext";
import { useNavigate } from "react-router-dom";
import { API_URL } from "../config";
export default function CreateRoomPage() {

  const {token, setToken} = useContext(AuthContext);
  const navigate = useNavigate();
  const [response, setResponse] = useState("");
  const [quizes, setQuizes] = useState([]);
  const [ChosenQuiz, setChosenQuiz] = useState("");

  useEffect(() =>{
    const fetch_quizes = async () =>{
    const res = await fetch(`${API_URL}/api/quizes_name/`, {
      method:"GET",
      })
    const data = await res.json()
    setQuizes(data)
    }
    fetch_quizes()
  },[])

  const create_room = async () => {
    try {
      const res = await fetch(`${API_URL}/api/create_room/`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          quiz_name: ChosenQuiz
        })
      });

      const data = await res.json();
      setResponse(data.room_code);
      navigate(`/LobbyRoom/${data.room_code}`);
    } catch (err) {
      setResponse(err);
    }
  };

    
return (
  <div className="h-screen w-screen flex flex-col items-center justify-center gap-10">
    
    <div className="font-semibold text-4xl text-white">
      Choose your quiz and create room
    </div>

    <div className="flex gap-6 flex-wrap justify-center px-10">
      {quizes.map((quiz_name, id) => (
        <button
          key={id}
          className="
            px-6 py-3
            text-white
            rounded-2xl
            shadow-md
            hover:bg-red-700
            hover:shadow-lg
            active:scale-95
            transition-all duration-200
            font-semibold
          "
          onClick={() => setChosenQuiz(quiz_name)}
        >
          {quiz_name}
        </button>
      ))}
    </div>

    <button
      className="
        rounded-2xl
        bg-orange-700
        text-white
        px-8
        py-4
        font-mono
        text-lg
        shadow-lg
        hover:bg-orange-600
        active:bg-orange-800
        active:scale-95
        transition-all
        duration-150
      "
      onClick={() => create_room()}
    >
      Create '{ChosenQuiz}' Quiz Room {response}
    </button>

  </div>
);}