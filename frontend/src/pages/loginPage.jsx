
import { useContext, useState } from "react";
import { AuthContext } from "../components/LoginContext";
import { API_URL } from "../config";
export default function LoginPage() {
  const {token, setToken } = useContext(AuthContext);
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [Reglogin, setRegLogin] = useState("");
  const [Regpassword, setRegPassword] = useState("");

  const loginUser = async (login, password) => {
    try {
      const response = await fetch(`${API_URL}/api/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: login, password }),
      });
      if (!response.ok) 
        throw new Error("login error");
      const data = await response.json();
      setToken(data.access);
    } catch (err) {
      console.error(err);
    }
  };

    const registerUser = async (regLogin, regPassword) => {
    const response = await fetch(`${API_URL}/api/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: regLogin, password: regPassword }),
    });

    if (!response.ok) {
        throw new Error("Registration failed");
    }

    const data = await response.json();
    setToken(data.access);  
    return data;
    };

  return (
    <div className="flex flex-row absolute top-[30vh] left-1/2 -translate-x-1/2 gap-50">
    <div className="flex flex-col items-center justify-center gap-10">
        <div className="font-mono ">LOGIN</div>
      <input
        className="bg-white rounded-xl text-black px-4 py-2"
        placeholder="login"
        value={login}
        onChange={(e) => setLogin(e.target.value)}
      />
      <input
        className="bg-white rounded-xl text-black px-4 py-2"
        placeholder="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="font-mono hover:bg-white" onClick={() => loginUser(login, password)}>Login</button>
      
    </div>
        <div className="flex flex-col items-center justify-center gap-10">
            <div className="font-mono ">REGISTER</div>
      <input
        className="bg-white rounded-xl text-black px-4 py-2"
        placeholder="login"
        value={Reglogin}
        onChange={(e) => setRegLogin(e.target.value)}
      />
      <input
        className="bg-white rounded-xl text-black px-4 py-2"
        placeholder="password"
        type="password"
        value={Regpassword}
        onChange={(e) => setRegPassword(e.target.value)}
      />
      <button className="font-mono hover:bg-white" onClick={() => registerUser(Reglogin, Regpassword)}>Register</button>
      
    </div>

    </div>
  );
}