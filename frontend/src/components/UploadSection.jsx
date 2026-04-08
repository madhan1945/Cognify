import { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { Upload, FileText, Loader, Settings } from 'lucide-react'

const API = 'http://localhost:8000/api/v1'

function CountInput({ label, value, onChange, color }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</p>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
        <button onClick={() => onChange(Math.max(1, value - 1))} style={{ width: '28px', height: '28px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-hover)', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1rem' }}>-</button>
        <span style={{ fontSize: '1.2rem', fontWeight: '700', color, minWidth: '24px', textAlign: 'center' }}>{value}</span>
        <button onClick={() => onChange(Math.min(15, value + 1))} style={{ width: '28px', height: '28px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-hover)', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1rem' }}>+</button>
      </div>
    </div>
  )
}

function UploadSection({ setQuiz, loading, setLoading }) {
  const [mode, setMode] = useState('text')
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [mcqCount, setMcqCount] = useState(5)
  const [tfCount, setTfCount] = useState(5)
  const [fillCount, setFillCount] = useState(5)

  const handleTextSubmit = async () => {
    if (text.trim().split(' ').length < 50) { toast.error('Please enter at least 50 words!'); return }
    setLoading(true)
    try {
      const res = await axios.post(`${API}/quiz/generate`, { content: text, mcq_count: mcqCount, tf_count: tfCount, fill_count: fillCount }, { headers: { 'Content-Type': 'application/json' } })
      setQuiz(res.data)
      toast.success(`Generated ${res.data.total_questions} questions!`)
    } catch { toast.error('Failed to generate quiz. Is the backend running?') }
    finally { setLoading(false) }
  }

  const handleFileSubmit = async () => {
    if (!file) { toast.error('Please select a file first!'); return }
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const uploadRes = await axios.post(`${API}/upload/file`, formData)
      const fullText = uploadRes.data.full_text || uploadRes.data.preview
      const quizRes = await axios.post(`${API}/quiz/generate`, { content: fullText, mcq_count: mcqCount, tf_count: tfCount, fill_count: fillCount }, { headers: { 'Content-Type': 'application/json' } })
      setQuiz(quizRes.data)
      toast.success(`Generated ${quizRes.data.total_questions} questions!`)
    } catch { toast.error('Failed to process file.') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ marginBottom: '2rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '2.5rem', paddingTop: '1rem' }}>
        <h2 style={{ fontSize: '2.5rem', fontWeight: '800', letterSpacing: '-1px', background: 'linear-gradient(135deg, #f0f0ff, #6c63ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '0.5rem' }}>Turn Any Content Into a Quiz</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>Paste text or upload a PDF/DOCX — Cognify does the rest</p>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '1.5rem', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-card)', padding: '6px', borderRadius: '12px', border: '1px solid var(--border)' }}>
          {['text', 'file'].map(m => (
            <button key={m} onClick={() => setMode(m)} style={{ padding: '8px 24px', borderRadius: '8px', border: 'none', background: mode === m ? 'var(--accent)' : 'transparent', color: mode === m ? '#fff' : 'var(--text-secondary)', fontWeight: '500', fontSize: '0.9rem', transition: 'all 0.2s', cursor: 'pointer' }}>
              {m === 'text' ? 'Paste Text' : 'Upload File'}
            </button>
          ))}
        </div>
        <button onClick={() => setShowSettings(!showSettings)} style={{ padding: '8px 16px', borderRadius: '10px', border: '1px solid var(--border)', background: showSettings ? 'var(--accent-glow)' : 'var(--bg-card)', color: showSettings ? 'var(--accent-light)' : 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', cursor: 'pointer' }}>
          <Settings size={14} /> Customize
        </button>
      </div>

      {showSettings && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem', marginBottom: '1rem', display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <CountInput label="MCQ" value={mcqCount} onChange={setMcqCount} color="var(--accent-light)" />
          <CountInput label="True / False" value={tfCount} onChange={setTfCount} color="var(--success)" />
          <CountInput label="Fill in Blank" value={fillCount} onChange={setFillCount} color="var(--warning)" />
          <div style={{ display: 'flex', alignItems: 'center', padding: '0 1rem', borderLeft: '1px solid var(--border)' }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total</p>
              <p style={{ fontSize: '1.4rem', fontWeight: '700', color: 'var(--text-primary)' }}>{mcqCount + tfCount + fillCount}</p>
            </div>
          </div>
        </div>
      )}

      {mode === 'text' && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem' }}>
          <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Paste your study material here — lecture notes, textbook content, articles..." style={{ width: '100%', minHeight: '200px', background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '10px', padding: '1rem', color: 'var(--text-primary)', fontSize: '0.9rem', resize: 'vertical', outline: 'none', lineHeight: '1.7' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{text.trim() ? text.trim().split(/\s+/).length : 0} words</span>
            <button onClick={handleTextSubmit} disabled={loading} style={{ padding: '10px 28px', borderRadius: '10px', border: 'none', background: loading ? 'var(--bg-hover)' : 'var(--accent)', color: '#fff', fontWeight: '600', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px', transition: 'all 0.2s', cursor: loading ? 'default' : 'pointer' }}>
              {loading ? <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} /> : null}
              {loading ? 'Generating...' : 'Generate Quiz'}
            </button>
          </div>
        </div>
      )}

      {mode === 'file' && (
        <div style={{ background: 'var(--bg-card)', border: `2px dashed ${dragOver ? 'var(--accent)' : 'var(--border)'}`, borderRadius: '16px', padding: '3rem', textAlign: 'center', transition: 'all 0.2s' }}
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={e => { e.preventDefault(); setDragOver(false); setFile(e.dataTransfer.files[0]) }}>
          {file ? (
            <div>
              <FileText size={40} color="var(--accent)" style={{ marginBottom: '1rem' }} />
              <p style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{file.name}</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>{(file.size / 1024).toFixed(1)} KB</p>
              <button onClick={handleFileSubmit} disabled={loading} style={{ padding: '10px 28px', borderRadius: '10px', border: 'none', background: loading ? 'var(--bg-hover)' : 'var(--accent)', color: '#fff', fontWeight: '600', fontSize: '0.95rem', cursor: loading ? 'default' : 'pointer' }}>
                {loading ? 'Processing...' : 'Generate Quiz'}
              </button>
            </div>
          ) : (
            <div>
              <Upload size={40} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
              <p style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Drop your file here</p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>PDF, DOCX, or TXT — max 10MB</p>
              <label style={{ padding: '10px 24px', borderRadius: '10px', border: '1px solid var(--accent)', color: 'var(--accent)', fontWeight: '500', cursor: 'pointer', fontSize: '0.9rem' }}>
                Browse Files
                <input type="file" accept=".pdf,.docx,.txt" style={{ display: 'none' }} onChange={e => setFile(e.target.files[0])} />
              </label>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default UploadSection
