
import { useContext, useState, useEffect } from "react";
import { AuthContext } from "../components/LoginContext";
import { useNavigate } from "react-router-dom";
import { API_URL } from "../config";
export default function CreateRoomPage() {

  const {token, setToken} = useContext(AuthContext);
  const navigate = useNavigate();
  const [response, setResponse] = useState("");

  const create_room = async () => {
    try{
      const res = await fetch(`${API_URL}/api/create_room/`, {
        method:"POST",
        headers:{
          "Authorization": `Bearer ${token}`
        }
      })
      const data = await res.json();
      setResponse(data.room_code);
      navigate(`/LobbyRoom/${data.room_code}`);

    }
    catch (err){
      setResponse(err);
    }
  };

    

  return (
    <div className="h-screen w-screen flex items-center justify-center">
      <button className="
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
      onClick={() => create_room()}>
        Create Quiz Room, {response}
      </button>
    </div>
  );
}