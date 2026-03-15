import { useEffect, useState, useContext, useRef } from "react";
import { AuthContext } from "../components/loginContext";
import { useParams} from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { API_URL } from "../config";
export default function RoomPage() {
  const { room_code } = useParams();
  const { token } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    let isEffectActive = true; 

    const socket = new WebSocket(`ws://localhost:8000/ws/room/${room_code}/?token=${token}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "users_list" && isEffectActive) {
        setUsers(data.users);
      }
    };

    socket.onopen = () => console.log("Connected to room", room_code);

    socket.onclose = (event) => {
      console.log("Disconnected, code:", event.code);
      
      const errorCodes = [4401, 4404, 1006];
      if (isEffectActive && errorCodes.includes(event.code)) {

        navigate("/PinPage");
      }
    };

    return () => {
      isEffectActive = false; 
      socket.close();
    };
  }, [room_code, token, navigate]);

  return (
    <div>
      <h1>Lobby Room: {room_code}</h1>
      <h2>Users in room:</h2>
      <ul>{users.map(u => <li key={u}>{u}</li>)}</ul>
    </div>
  );
}