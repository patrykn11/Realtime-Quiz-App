import { useEffect, useState, useContext, useRef } from "react";
import { AuthContext } from "../components/loginContext";
import { useParams} from "react-router-dom";
import { useNavigate } from "react-router-dom";
import UserBlock from "../components/userBlock";

export default function QuizPage(){
  const { room_code } = useParams();
  const {question, setQuestion} = useState("");
  const {answers, setAnswers} = useState("");
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();
  useEffect(()=>{
    let isEffectActive = true; 

    const socket = new WebSocket(`ws://localhost:8000/ws/room/${room_code}/?token=${token}`);

    socket.onmessage = (event) =>{
        data = JSON.parse(event.data)
        if (data.type === "question" && isEffectActive) {
            setQuestion(data.question);
            setAnswers(data.answers);
      }

    }

    socket.onclose = () =>{
        if (isEffectActive){
            navigate("/PinPage");
        }
    }

    return () => {
      isEffectActive = false; 
      socket.close();
    };

  })
}