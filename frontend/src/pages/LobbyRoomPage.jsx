import { useEffect, useState, useContext, useRef } from "react";
import { AuthContext } from "../components/LoginContext";
import { useParams, useNavigate } from "react-router-dom";
import UserBlock from "../components/UserBlock";

export default function RoomPage() {
  const { room_code } = useParams();
  const { token } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  const socketRef = useRef(null);

  useEffect(() => {
    let isEffectActive = true;

    socketRef.current = new WebSocket(
      `ws://localhost:8000/ws/room/${room_code}/?token=${token}`
    );

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "users_list" && isEffectActive) {
        setUsers(data.users);
      }
      if (data.type === "game_started" && isEffectActive) {
        navigate(`/QuizPage/${room_code}`);
         
      }
    };

    socketRef.current.onopen = () => console.log("Connected to room", room_code);

    socketRef.current.onclose = (event) => {
      console.log("Disconnected, code:", event.code);

      const errorCodes = [4401, 4404, 1006];
      if (isEffectActive && errorCodes.includes(event.code)) {
        navigate("/PinPage");
      }
    };

    return () => {
      isEffectActive = false;
      socketRef.current.close();
    };
  }, [room_code, token, navigate]);
  const sendMessage = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type:"start_game"
      };
      socketRef.current.send(JSON.stringify(message));
      console.log("send:", message);
    } else {
      console.log("error");
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center py-10">
      <div className="w-full max-w-3xl px-6">
        <h1 className="text-3xl font-bold text-white mb-6 ml-2">Lobby : {room_code}</h1>
        <div className="bg-gray-300 rounded-3xl p-6 shadow-2xl flex flex-col gap-4">
          {users.map((user, index) => (
            <UserBlock key={index} name={user} />
          ))}
          <button onClick={sendMessage}>GRAJ</button>
        </div>
      </div>
    </div>
  );
}