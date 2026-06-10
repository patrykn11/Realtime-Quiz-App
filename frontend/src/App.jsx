import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import "./App.css";
import { AuthProvider } from "./components/LoginContext";
import MainLayout from "./layout/MainLayout";
import CreateRoomPage from "./pages/CreateRoomPage";
import CreateQuizPage from "./pages/CreateQuizPage";
import EditQuizPage from "./pages/EditQuizPage";
import LobbyRoomPage from "./pages/LobbyRoomPage";
import LoginPage from "./pages/LoginPage";
import PinPage from "./pages/PinPage";
import ProfilePage from "./pages/ProfilePage";
import QuizHistoryRankingPage from "./pages/QuizHistoryRankingPage";
import QuizPage from "./pages/QuizPage";
import RegisterPage from "./pages/RegisterPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/join" replace />} />
            <Route path="join" element={<PinPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="create-room" element={<CreateRoomPage />} />
            <Route path="create-quiz" element={<CreateQuizPage />} />
            <Route path="quizzes/:quizId/edit" element={<EditQuizPage />} />
            <Route path="lobby/:room_code" element={<LobbyRoomPage />} />
            <Route path="quiz/:room_code" element={<QuizPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="profile/history/:gameId" element={<QuizHistoryRankingPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
