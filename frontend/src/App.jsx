import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PinPage from './pages/pinPage'
import MainLayout from './Layout/MainLayout';
import LoginPage from './pages/loginPage';
import { AuthProvider } from './components/loginContext';
import CreateRoomPage from './pages/createRoomPage';
import LobbyRoomPage from './pages/LobbyRoomPage'
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
      </Route>
    </Routes>
    </AuthProvider>
    </BrowserRouter>
  )
}

export default App
