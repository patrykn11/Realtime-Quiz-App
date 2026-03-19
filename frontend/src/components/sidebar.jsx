import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./LoginContext";

const Sidebar = () => {
  const items = [
    { name: "Home", path: "/pinPage" },
    { name: "Create room", path: "/createRoom" },
    { name: "Join Room", path: "/pinPage" }
  ];

  const { token, setToken } = useContext(AuthContext);
  const navigate = useNavigate();

  const logout = () => {
    setToken("");
    navigate("/loginPage");
  };

  return (
    <div className="w-64 h-screen bg-linear-to-r from-[#693620] to-[#9e3636] text-white flex flex-col p-4 shadow-xl">

      <div className="flex flex-col gap-10 py-10">
        {items.map((item) => (
          <button
            key={item.name}
            onClick={() => navigate(item.path)}
            className="hover:bg-black font-mono"
          >
            {item.name}
          </button>
        ))}

         <div className="flex flex-col gap-10">
          {token ? (
            <button onClick={logout} className="hover:bg-black font-mono">
              Logout
            </button>
          ) : (
            <button  onClick={() => navigate("/loginPage")} className="hover:bg-black font-mono">
              Sign in
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;