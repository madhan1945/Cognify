import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import UploadSection from './components/UploadSection'
import QuizSection from './components/QuizSection'
import StatsBar from './components/StatsBar'
import './index.css'

function App() {
  const [quiz, setQuiz] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
          },
        }}
      />
      <Header />
      <main style={{ maxWidth: '1100px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        <UploadSection setQuiz={setQuiz} loading={loading} setLoading={setLoading} />
        {quiz && <StatsBar quiz={quiz} />}
        {quiz && <QuizSection quiz={quiz} />}
      </main>
    </div>
  )
}

export default App