import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PinPage from './pages/pinPage'
import MainLayout from './Layout/MainLayout';

function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<MainLayout />} >
        <Route path='pinPage' element={<PinPage/>} />
        <Route path='createRoom' /* element={<CreateRoomPage/>}*//>
        <Route path='lobbyRoom' /*element={<LobbyRoomPage/>}*//>
      </Route>
    </Routes>
    </BrowserRouter>
  )
}

export default App
