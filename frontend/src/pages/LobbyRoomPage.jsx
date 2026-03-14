import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../components/loginContext";
import { useParams } from "react-router-dom";

export default function RoomPage() {
  const { room_code } = useParams();
  const { token } = useContext(AuthContext);
  const [users, setUsers] = useState([]);

    useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/room/${room_code}/?token=${token}`);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "users_list") {
        setUsers(data.users);
        }
    };

    socket.onopen = () => console.log("Connected to room", room_code);

    socket.onclose = () => console.log("Disconnected");

    return () => socket.close();
    }, [room_code, token]);

  return (
    <div>
      <h1>Lobby Room: {room_code}</h1>
      <h2>Users in room:</h2>
      <ul>{users.map(u => <li key={u}>{u}</li>)}</ul>
    </div>
  );
}