import { useContext } from "react";
import { useNavigate } from "react-router-dom";

import { AuthContext } from "./LoginContext";

const navigationItems = [
  { name: "Join room", path: "/join" },
  { name: "Create room", path: "/create-room" },
];

export default function Sidebar() {
  const { token, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <aside className="flex w-full flex-shrink-0 flex-col bg-linear-to-r from-[#693620] to-[#9e3636] p-4 text-white shadow-xl md:h-screen md:w-64">
      <nav className="flex flex-row flex-wrap justify-center gap-4 py-4 md:flex-col md:gap-10 md:py-10">
        {navigationItems.map((item) => (
          <button
            key={item.name}
            onClick={() => navigate(item.path)}
            className="font-mono hover:bg-black"
          >
            {item.name}
          </button>
        ))}
        {token && (
          <button
            onClick={() => navigate("/create-quiz")}
            className="font-mono hover:bg-black"
          >
            Create quiz
          </button>
        )}
      </nav>

      <div className="flex flex-row flex-wrap justify-center gap-4 border-white/20 pt-4 md:mt-auto md:flex-col md:border-t md:pb-6">
        {token ? (
          <>
            <button onClick={() => navigate("/profile")} className="font-mono hover:bg-black">
              Profile
            </button>
            <button onClick={handleLogout} className="font-mono hover:bg-black">
              Logout
            </button>
          </>
        ) : (
          <>
            <button onClick={() => navigate("/login")} className="font-mono hover:bg-black">
              Sign in
            </button>
            <button onClick={() => navigate("/register")} className="font-mono hover:bg-black">
              Register
            </button>
          </>
        )}
      </div>
    </aside>
  );
}
