import { useState } from 'react'
import { CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'

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

function QuestionCard({ question, index }) {
  const [selected, setSelected] = useState(null)
  const [revealed, setRevealed] = useState(false)
  const [expanded, setExpanded] = useState(true)

  const isCorrect = selected === question.answer

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: '16px',
      marginBottom: '1rem',
      overflow: 'hidden',
      transition: 'all 0.2s',
    }}>
      {/* Card Header */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '1rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          borderBottom: expanded ? '1px solid var(--border)' : 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{
            width: '28px',
            height: '28px',
            borderRadius: '8px',
            background: 'var(--accent-glow)',
            border: '1px solid var(--accent)',
            color: 'var(--accent-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.8rem',
            fontWeight: '700',
            flexShrink: 0,
          }}>{index + 1}</span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{
              padding: '2px 10px',
              borderRadius: '20px',
              background: 'var(--bg-hover)',
              color: 'var(--text-secondary)',
              fontSize: '0.72rem',
              fontWeight: '500',
            }}>{typeLabel[question.type] || question.type}</span>
            <span style={{
              padding: '2px 10px',
              borderRadius: '20px',
              background: `${difficultyColor[question.difficulty]}20`,
              color: difficultyColor[question.difficulty],
              fontSize: '0.72rem',
              fontWeight: '600',
            }}>{question.difficulty}</span>
          </div>
        </div>
        {expanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
      </div>

      {/* Card Body */}
      {expanded && (
        <div style={{ padding: '1.5rem' }}>
          <p style={{
            fontSize: '0.95rem',
            fontWeight: '500',
            marginBottom: '1.2rem',
            lineHeight: '1.6',
            color: 'var(--text-primary)',
          }}>
            {question.question}
          </p>

          {/* MCQ Options */}
          {question.type === 'mcq' && question.options && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '1rem' }}>
              {question.options.map((opt, i) => {
                const isSelected = selected === opt
                const isAnswer = revealed && opt === question.answer
                const isWrong = revealed && isSelected && opt !== question.answer

                return (
                  <button key={i} onClick={() => !revealed && setSelected(opt)} style={{
                    padding: '10px 16px',
                    borderRadius: '10px',
                    border: `1px solid ${isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent)' : 'var(--border)'}`,
                    background: isAnswer ? 'rgba(74, 222, 128, 0.1)' : isWrong ? 'rgba(248, 113, 113, 0.1)' : isSelected ? 'var(--accent-glow)' : 'var(--bg-secondary)',
                    color: isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent-light)' : 'var(--text-secondary)',
                    fontSize: '0.85rem',
                    fontWeight: '500',
                    textAlign: 'left',
                    cursor: revealed ? 'default' : 'pointer',
                    transition: 'all 0.2s',
                  }}>
                    {opt}
                  </button>
                )
              })}
            </div>
          )}

          {/* True/False Options */}
          {question.type === 'true_false' && (
            <div style={{ display: 'flex', gap: '8px', marginBottom: '1rem' }}>
              {['True', 'False'].map(opt => {
                const isSelected = selected === opt
                const isAnswer = revealed && opt === question.answer
                const isWrong = revealed && isSelected && opt !== question.answer

                return (
                  <button key={opt} onClick={() => !revealed && setSelected(opt)} style={{
                    padding: '10px 28px',
                    borderRadius: '10px',
                    border: `1px solid ${isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent)' : 'var(--border)'}`,
                    background: isAnswer ? 'rgba(74, 222, 128, 0.1)' : isWrong ? 'rgba(248, 113, 113, 0.1)' : isSelected ? 'var(--accent-glow)' : 'var(--bg-secondary)',
                    color: isAnswer ? 'var(--success)' : isWrong ? 'var(--danger)' : isSelected ? 'var(--accent-light)' : 'var(--text-secondary)',
                    fontSize: '0.9rem',
                    fontWeight: '600',
                    cursor: revealed ? 'default' : 'pointer',
                    transition: 'all 0.2s',
                  }}>
                    {opt}
                  </button>
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
                  width: '100%',
                  padding: '10px 16px',
                  borderRadius: '10px',
                  border: '1px solid var(--border)',
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  outline: 'none',
                }}
              />
            </div>
          )}

          {/* Reveal / Result */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '0.5rem' }}>
            {!revealed ? (
              <button onClick={() => setRevealed(true)} style={{
                padding: '8px 20px',
                borderRadius: '8px',
                border: '1px solid var(--border)',
                background: 'var(--bg-hover)',
                color: 'var(--text-secondary)',
                fontSize: '0.85rem',
                fontWeight: '500',
                transition: 'all 0.2s',
              }}>
                Reveal Answer
              </button>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {isCorrect
                  ? <CheckCircle size={18} color="var(--success)" />
                  : <XCircle size={18} color="var(--danger)" />
                }
                <span style={{
                  fontSize: '0.85rem',
                  color: isCorrect ? 'var(--success)' : 'var(--danger)',
                  fontWeight: '500',
                }}>
                  {isCorrect ? 'Correct!' : `Answer: ${question.answer}`}
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

  const filtered = filter === 'all'
    ? quiz.questions
    : quiz.questions.filter(q => q.type === filter)

  return (
    <div>
      {/* Filter Bar */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '1.5rem',
        flexWrap: 'wrap',
      }}>
        {['all', 'mcq', 'true_false', 'fill_blank'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            padding: '6px 16px',
            borderRadius: '20px',
            border: `1px solid ${filter === f ? 'var(--accent)' : 'var(--border)'}`,
            background: filter === f ? 'var(--accent-glow)' : 'transparent',
            color: filter === f ? 'var(--accent-light)' : 'var(--text-secondary)',
            fontSize: '0.82rem',
            fontWeight: '500',
            transition: 'all 0.2s',
          }}>
            {f === 'all' ? 'All' : typeLabel[f]}
            <span style={{
              marginLeft: '6px',
              padding: '1px 6px',
              borderRadius: '10px',
              background: 'var(--bg-hover)',
              fontSize: '0.75rem',
            }}>
              {f === 'all' ? quiz.questions.length : quiz.questions.filter(q => q.type === f).length}
            </span>
          </button>
        ))}
      </div>

      {/* Questions */}
      {filtered.map((q, i) => (
        <QuestionCard key={i} question={q} index={i} />
      ))}
    </div>
  )
}

export default QuizSection