import { Route, Routes } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Sidebar } from './components/Sidebar'
import { Budget } from './pages/Budget'
import { Dashboard } from './pages/Dashboard'
import { Food } from './pages/Food'
import { History } from './pages/History'
import { Judging } from './pages/Judging'
import { Messages } from './pages/Messages'
import { Schedule } from './pages/Schedule'
import { Trace } from './pages/Trace'
import { Validation } from './pages/Validation'
import { Venue } from './pages/Venue'

function App() {
  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <main className="mx-auto max-w-6xl p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/venue" element={<Venue />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/food" element={<Food />} />
            <Route path="/judging" element={<Judging />} />
            <Route path="/budget" element={<Budget />} />
            <Route path="/trace" element={<Trace />} />
            <Route path="/validation" element={<Validation />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
