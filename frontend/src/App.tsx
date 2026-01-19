import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Setup from './pages/Setup'
import Workflow from './pages/Workflow'
import Chat from './pages/Chat'
import { useStore } from './store/useStore'

function App() {
  const { createSession, sessionId } = useStore()

  useEffect(() => {
    if (!sessionId) {
      createSession()
    }
  }, [sessionId, createSession])

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="setup" element={<Setup />} />
        <Route path="workflow" element={<Workflow />} />
        <Route path="chat" element={<Chat />} />
      </Route>
    </Routes>
  )
}

export default App
