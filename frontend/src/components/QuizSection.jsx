import { useState } from 'react'
import { CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'
import axios from 'axios'

const API = 'http://localhost:8000/api/v1'

const difficultyColor = {
  easy: 'var(--easy)',
  medium: 'var(--medium)',
  hard: 'var(--hard)',
}

const typeLabel = {
  mcq: 'MCQ',
  true_false: 'True / False',
  fill_blank: 'Fill in Blank',
  short_answer: 'Short Answer',
}

function QuestionCard({ question, index, onAnswer, quiz_id }) {
  const [selected, setSelected] = useState(null)
  const [revealed, setRevealed] = useState(false)
  const [evaluation, setEvaluation] = useState(null)
  const [expanded, setExpanded] = useState(true)

  const handleReveal = async () => {
    if (!selected && question.type !== 'true_false') {
      setRevealed(true)
      setEvaluation({
        is_correct: false,
        feedback: `Correct answer: ${question.answer}`,
        score: 0,
      })
      onAnswer && onAnswer(false)
      try {
        await axios.post(`${API}/adaptive/record`, {
          session_id: quiz_id || 'anonymous',
          question_type: question.type,
          difficulty: question.difficulty,
          is_correct: false,
          topic: 'General',
        })
      } catch {}
      return
    }

    try {
      const res = await axios.post(`${API}/evaluate/answer`, {
        question_type: question.type,
        user_answer: selected || '',
        correct_answer: question.answer,
      })
      setEvaluation(res.data)
      setRevealed(true)
      onAnswer && onAnswer(res.data.is_correct)
      await axios.post(`${API}/adaptive/record`, {
        session_id: quiz_id || 'anonymous',
        question_type: question.type,
        difficulty: question.difficulty,
        is_correct: res.data.is_correct,
        topic: 'General',
      })
    } catch {
      setRevealed(true)
      const isCorrect = selected?.toLowerCase() === question.answer?.toLowerCase()
      setEvaluation({
        is_correct: isCorrect,
        feedback: isCorrect ? 'Correct!' : `Correct answer: ${question.answer}`,
        score: isCorrect ? 1 : 0,
      })
      onAnswer && onAnswer(isCorrect)
    }
  }

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: `1px solid ${revealed ? (evaluation?.is_correct ? 'rgba(74,222,128,0.3)' : 'rgba(248,113,113,0.3)') : 'var(--border)'}`,
      borderRadius: '16px',
      marginBottom: '1rem',
      overflow: 'hidden',
      transition: 'all 0.3s',
    }}>
      {/* Header */}
      <div onClick={() => setExpanded(!expanded)} style={{
        padding: '1rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: 'pointer',
        borderBottom: expanded ? '1px solid var(--border)' : 'none',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            width: '28px', height: '28px', borderRadius: '8px',
            background: 'var(--accent-glow)', border: '1px solid var(--accent)',
            color: 'var(--accent-light)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: '0.8rem', fontWeight: '700', flexShrink: 0,
          }}>{index + 1}</span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{
              padding: '2px 10px', borderRadius: '20px',
              background: 'var(--bg-hover)', color: 'var(--text-secondary)',
              fontSize: '0.72rem', fontWeight: '500',
            }}>{typeLabel[question.type] || question.type}</span>
            <span style={{
              padding: '2px 10px', borderRadius: '20px',
              background: `${difficultyColor[question.difficulty]}20`,
              color: difficultyColor[question.difficulty],
              fontSize: '0.72rem', fontWeight: '600',
            }}>{question.difficulty}</span>
            {revealed && (
              <span style={{
                padding: '2px 10px', borderRadius: '20px',
                background: evaluation?.is_correct ? 'rgba(74,222,128,0.1)' : 'rgba(248,113,113,0.1)',
                color: evaluation?.is_correct ? 'var(--success)' : 'var(--danger)',
                fontSize: '0.72rem', fontWeight: '600',
              }}>{evaluation?.is_correct ? '✓ Correct' : '✗ Wrong'}</span>
            )}
          </div>
        </div>
        {expanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
      </div>

      {/* Body */}
      {expanded && (
        <div style={{ padding: '1.5rem' }}>
          <p style={{
            fontSize: '0.95rem', fontWeight: '500',
            marginBottom: '1.2rem', lineHeight: '1.6',
          }}>{question.question}</p>

          {/* MCQ */}
          {question.type === 'mcq' && question.options && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '1rem' }}>
              {question.options.map((opt, i) => {
                const isSelected = selected === opt
                const isAnswer = revealed && opt === question.answer
                const isWrong = revealed && isSelected && opt !== question.answer
                return (
                  <button key={i} onClick={() => !revealed && setSelected(opt)} style={{
                    padding: '10px 16px', borderRadius: '10px', textAlign: 'left',
                    border: `1px solid ${isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent)' : 'var(--border)'}`,
                    background: isAnswer ? 'rgba(74,222,128,0.1)' : isWrong ? 'rgba(248,113,113,0.1)' : isSelected ? 'var(--accent-glow)' : 'var(--bg-secondary)',
                    color: isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent-light)' : 'var(--text-secondary)',
                    fontSize: '0.85rem', fontWeight: '500',
                    cursor: revealed ? 'default' : 'pointer', transition: 'all 0.2s',
                  }}>{opt}</button>
                )
              })}
            </div>
          )}

          {/* True/False */}
          {question.type === 'true_false' && (
            <div style={{ display: 'flex', gap: '8px', marginBottom: '1rem' }}>
              {['True', 'False'].map(opt => {
                const isSelected = selected === opt
                const isAnswer = revealed && opt === question.answer
                const isWrong = revealed && isSelected && opt !== question.answer
                return (
                  <button key={opt} onClick={() => !revealed && setSelected(opt)} style={{
                    padding: '10px 28px', borderRadius: '10px',
                    border: `1px solid ${isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent)' : 'var(--border)'}`,
                    background: isAnswer ? 'rgba(74,222,128,0.1)' : isWrong ? 'rgba(248,113,113,0.1)' : isSelected ? 'var(--accent-glow)' : 'var(--bg-secondary)',
                    color: isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent-light)' : 'var(--text-secondary)',
                    fontSize: '0.9rem', fontWeight: '600',
                    cursor: revealed ? 'default' : 'pointer', transition: 'all 0.2s',
                  }}>{opt}</button>
                )
              })}
            </div>
          )}

          {/* Fill in Blank */}
          {question.type === 'fill_blank' && (
            <div style={{ marginBottom: '1rem' }}>
              <input
                type="text"
                placeholder="Type your answer..."
                onChange={e => setSelected(e.target.value)}
                disabled={revealed}
                style={{
                  width: '100%', padding: '10px 16px', borderRadius: '10px',
                  border: `1px solid ${revealed ? (evaluation?.is_correct ? 'var(--success)' : 'var(--danger)') : 'var(--border)'}`,
                  background: 'var(--bg-secondary)', color: 'var(--text-primary)',
                  fontSize: '0.9rem', outline: 'none',
                }}
              />
            </div>
          )}

          {/* Feedback */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '0.5rem' }}>
            {!revealed ? (
              <button onClick={handleReveal} style={{
                padding: '8px 20px', borderRadius: '8px',
                border: '1px solid var(--border)', background: 'var(--bg-hover)',
                color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '500',
              }}>
                {selected ? 'Submit Answer' : 'Reveal Answer'}
              </button>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {evaluation?.is_correct
                  ? <CheckCircle size={18} color="var(--success)" />
                  : <XCircle size={18} color="var(--danger)" />
                }
                <span style={{
                  fontSize: '0.85rem', fontWeight: '500',
                  color: evaluation?.is_correct ? 'var(--success)' : 'var(--danger)',
                }}>
                  {evaluation?.feedback}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function QuizSection({ quiz }) {
  const [filter, setFilter] = useState('all')
  const [score, setScore] = useState({ correct: 0, total: 0 })
  const [sessionSaved, setSessionSaved] = useState(false)
  const [recommendation, setRecommendation] = useState(null)

  const handleAnswer = (isCorrect) => {
    setScore(prev => ({
      correct: prev.correct + (isCorrect ? 1 : 0),
      total: prev.total + 1,
    }))
  }

  const handleSaveSession = async () => {
    const pct = score.total > 0 ? Math.round((score.correct / score.total) * 100) : 0
    const grade = pct >= 90 ? 'A' : pct >= 80 ? 'B' : pct >= 70 ? 'C' : pct >= 60 ? 'D' : 'F'
    try {
      await axios.post(`${API}/sessions/save`, {
        quiz_id: quiz.quiz_id,
        questions: quiz.questions,
        answers: [],
        score: score.correct,
        percentage: pct,
        grade: grade,
        topic: 'General',
      })
      setSessionSaved(true)

      // Fetch recommendation after saving
      const rec = await axios.get(`${API}/adaptive/recommend`)
      setRecommendation(rec.data)
    } catch {
      alert('Failed to save session.')
    }
  }

  const filtered = filter === 'all'
    ? quiz.questions
    : quiz.questions.filter(q => q.type === filter)

  const percentage = score.total > 0 ? Math.round((score.correct / score.total) * 100) : 0

  return (
    <div>
      {/* Score Bar */}
      {score.total > 0 && (
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--border)',
          borderRadius: '14px', padding: '1rem 1.5rem',
          marginBottom: '1.5rem', display: 'flex',
          alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Score: <strong style={{ color: 'var(--text-primary)' }}>{score.correct}/{score.total}</strong>
            </span>
            <div style={{
              width: '200px', height: '6px',
              background: 'var(--bg-hover)', borderRadius: '3px',
            }}>
              <div style={{
                width: `${percentage}%`, height: '100%',
                background: percentage >= 70 ? 'var(--success)' : percentage >= 40 ? 'var(--warning)' : 'var(--danger)',
                borderRadius: '3px', transition: 'width 0.4s ease',
              }} />
            </div>
            <span style={{
              fontSize: '0.9rem', fontWeight: '600',
              color: percentage >= 70 ? 'var(--success)' : percentage >= 40 ? 'var(--warning)' : 'var(--danger)',
            }}>{percentage}%</span>
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {['all', 'mcq', 'true_false', 'fill_blank'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            padding: '6px 16px', borderRadius: '20px',
            border: `1px solid ${filter === f ? 'var(--accent)' : 'var(--border)'}`,
            background: filter === f ? 'var(--accent-glow)' : 'transparent',
            color: filter === f ? 'var(--accent-light)' : 'var(--text-secondary)',
            fontSize: '0.82rem', fontWeight: '500', transition: 'all 0.2s',
          }}>
            {f === 'all' ? 'All' : typeLabel[f]}
            <span style={{
              marginLeft: '6px', padding: '1px 6px',
              borderRadius: '10px', background: 'var(--bg-hover)', fontSize: '0.75rem',
            }}>
              {f === 'all' ? quiz.questions.length : quiz.questions.filter(q => q.type === f).length}
            </span>
          </button>
        ))}
      </div>

      {/* Questions */}
      {filtered.map((q, i) => (
        <QuestionCard key={i} question={q} index={i} onAnswer={handleAnswer} quiz_id={quiz.quiz_id} />
      ))}

      {/* Save Session */}
      {score.total > 0 && (
        <div style={{
          textAlign: 'center', marginTop: '2rem', padding: '1.5rem',
          background: 'var(--bg-card)', border: '1px solid var(--border)',
          borderRadius: '16px',
        }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: '700', marginBottom: '0.5rem' }}>
            {score.total === quiz.questions.length ? 'Quiz Complete! 🎉' : `${score.total} of ${quiz.questions.length} answered`}
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Score: {score.correct}/{score.total} ({percentage}%)
          </p>
          <button
            onClick={handleSaveSession}
            disabled={sessionSaved}
            style={{
              padding: '12px 32px', borderRadius: '10px', border: 'none',
              background: sessionSaved ? 'var(--bg-hover)' : 'var(--accent)',
              color: sessionSaved ? 'var(--text-muted)' : '#fff',
              fontWeight: '600', fontSize: '1rem', cursor: sessionSaved ? 'default' : 'pointer',
            }}>
            {sessionSaved ? 'Session Saved ✅' : 'Save Session'}
          </button>

          {/* Adaptive Recommendation */}
          {recommendation && (
            <div style={{
              marginTop: '1.5rem', padding: '1rem',
              background: 'var(--bg-secondary)', borderRadius: '12px',
              border: '1px solid var(--accent)',
            }}>
              <p style={{ fontSize: '0.9rem', color: 'var(--accent-light)', fontWeight: '600', marginBottom: '4px' }}>
                🧠 Adaptive Recommendation
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {recommendation.message}
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Overall accuracy: <strong style={{ color: 'var(--text-primary)' }}>{recommendation.overall_accuracy}%</strong>
              </p>
              {recommendation.weak_areas?.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Weak areas:</p>
                  {recommendation.weak_areas.map((area, i) => (
                    <p key={i} style={{ fontSize: '0.8rem', color: 'var(--danger)' }}>
                      • {area.area} ({area.accuracy}%) — {area.suggestion}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default QuizSection