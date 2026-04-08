import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import { BarChart2 } from 'lucide-react'
import Header from './components/Header'
import UploadSection from './components/UploadSection'
import QuizSection from './components/QuizSection'
import StatsBar from './components/StatsBar'
import Analytics from './components/Analytics'
import './index.css'

function App() {
  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Toaster position="top-right" toastOptions={{ style: { background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' } }} />
      <Header onAnalytics={() => setShowAnalytics(!showAnalytics)} showAnalytics={showAnalytics} />
      <main style={{ maxWidth: '1100px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        {showAnalytics ? (
          <Analytics onClose={() => setShowAnalytics(false)} />
        ) : (
          <>
            <UploadSection setQuiz={setQuiz} loading={loading} setLoading={setLoading} />
            {quiz && <StatsBar quiz={quiz} />}
            {quiz && <QuizSection quiz={quiz} />}
          </>
        )}
      </main>
    </div>
  )
}

export default App
