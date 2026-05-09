import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PinPage from './pages/PinPage'
import MainLayout from './Layout/MainLayout';
import LoginPage from './pages/LoginPage';
import { AuthProvider } from './components/LoginContext';
import CreateRoomPage from './pages/CreateRoomPage';
import LobbyRoomPage from './pages/LobbyRoomPage'
import QuizPage from './pages/QuizPage'
import ProfilePage from './pages/Profilepage';
import QuizHistoryRankingPage from './pages/QuizHistoryRankingPage';

function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
    <AuthProvider>
    <Routes>
      <Route path="/" element={<MainLayout />} >
        <Route path='pinPage' element={<PinPage/>} />
        <Route path='loginPage' element={<LoginPage/>} />
        <Route path='createRoom' element={<CreateRoomPage/>}/>
        <Route path='LobbyRoom/:room_code' element={<LobbyRoomPage/>}/>
        <Route path='QuizPage/:room_code' element={<QuizPage/>}/>
        <Route path='Profile' element={<ProfilePage/>}/>
        <Route path='Profile/history/:historyId' element={<QuizHistoryRankingPage/>}/>

      </Route>
    </Routes>
    </AuthProvider>
    </BrowserRouter>
  )
}

export default App
