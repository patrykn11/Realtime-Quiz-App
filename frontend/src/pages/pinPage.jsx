import React, { useState, useEffect } from "react";
import {useNavigate} from "react-router-dom";


export default function PinPage() {
  const [code, setCode] = useState("0000");
  const navigate = useNavigate();
  const [quizes, setQuizes] = useState([]);

  const join_room = async () =>{
    navigate(`/LobbyRoom/${code}`);
  }

  // Niesprawdzone
  // useEffect(() =>{
  //   const fetch_quizes = async () =>{
  //   const res = await fetch(`${API_URL}/api/quizes_name/`, {
  //     method:"GET",
  //     })
  //   const data = await res.json()
  //   setQuizes(data)
  //   }
  //   fetch_quizes()
    
    

  // }, [])
  return (
    
      <div className="absolute top-[30vh] left-1/2 -translate-x-1/2 flex flex-col items-center justify-center text-white text-xl p-1 gap-10 w-full max-w-md">
        <div className="font-mono text-5xl font-bold tracking-tight">Enter room PIN</div>
        <div className="gap-1 flex flex-row w-full px-4">
          <input 
            className="bg-white rounded-xl text-black px-4 py-2"
            placeholder="0000"
            onChange={(e) => setCode(e.target.value)} 
          />
          <button className="bg-white text-black px-6 rounded-xl" onClick={join_room}>
            Send
          </button>
        </div>
      </div>
  );
}