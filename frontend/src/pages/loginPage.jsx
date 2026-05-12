
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
    <div className="min-h-screen w-full flex flex-col items-center justify-center gap-12 px-4 py-10 text-white lg:flex-row lg:gap-24">
    <div className="flex w-full max-w-xs flex-col items-center justify-center gap-6">
        <div className="font-mono ">LOGIN</div>
      <input
        className="w-full bg-white rounded-xl text-black px-4 py-2"
        placeholder="login"
        value={login}
        onChange={(e) => setLogin(e.target.value)}
      />
      <input
        className="w-full bg-white rounded-xl text-black px-4 py-2"
        placeholder="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="font-mono hover:bg-white" onClick={() => loginUser(login, password)}>Login</button>
      
    </div>
        <div className="flex w-full max-w-xs flex-col items-center justify-center gap-6">
            <div className="font-mono ">REGISTER</div>
      <input
        className="w-full bg-white rounded-xl text-black px-4 py-2"
        placeholder="login"
        value={Reglogin}
        onChange={(e) => setRegLogin(e.target.value)}
      />
      <input
        className="w-full bg-white rounded-xl text-black px-4 py-2"
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
