import { Route, Routes } from 'react-router-dom'
import RegisterPage from './pages/RegisterPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<h1>Asosiy Sahifa</h1>} />
      <Route path="/login" element={<h1>Kirish Sahifasi</h1>} />
      <Route path="/register" element={<RegisterPage />} />
    </Routes>
  )
}

export default App
