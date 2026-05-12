import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "./LoginContext";

const Sidebar = () => {
  const items = [
    { name: "Home", path: "/pinPage" },
    { name: "Create room", path: "/createRoom" },
    { name: "Join Room", path: "/pinPage" },
  ];

  const { token, setToken } = useContext(AuthContext);
  const navigate = useNavigate();

  const logout = () => {
    setToken("");
    navigate("/loginPage");
  };

  const profile = () => {
    navigate("/Profile")
  }
  return (
    <div className="w-full md:w-64 md:h-screen bg-linear-to-r from-[#693620] to-[#9e3636] text-white flex-shrink-0 flex flex-col p-4 shadow-xl">

      <div className="flex flex-row flex-wrap justify-center gap-4 py-4 md:flex-col md:gap-10 md:py-10">
        {items.map((item) => (
          <button
            key={item.name}
            onClick={() => navigate(item.path)}
            className="hover:bg-black font-mono"
          >
            {item.name}
          </button>
        ))}

         <div className="flex flex-row flex-wrap justify-center gap-4 md:flex-col md:gap-10">
          {token ? (<>
            <button onClick={logout} className="hover:bg-black font-mono">
              Logout
            </button>
            <button onClick={profile} className="hover:bg-black font-mono">
              Profile
            </button>
            </>
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
