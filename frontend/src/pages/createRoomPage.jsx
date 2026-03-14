
import { useContext, useState, useEffect } from "react";
import { AuthContext } from "../components/loginContext";
import { API_URL } from "../config";
export default function CreateRoomPage() {

  const {token, setToken} = useContext(AuthContext);
  const [response, setResponse] = useState("");

  useEffect(() => {

    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/simple_endpoint`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        const data = await res.json();
        setResponse(data.status);

      } catch (err) {
        console.error(err);
      }
    };

    fetchData();

  }, [token]);

    

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
      ">
        Create Quiz Room, {response}
      </button>
    </div>
  );
}