import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000/api/v1'

function StatCard({ label, value, color, suffix = '' }) {
  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem', textAlign: 'center', borderTop: `3px solid ${color}` }}>
      <p style={{ fontSize: '2rem', fontWeight: '700', fontFamily: 'Syne, sans-serif', color, lineHeight: 1, marginBottom: '6px' }}>{value}{suffix}</p>
      <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</p>
    </div>
  )
}

function BarChart({ data, title }) {
  const max = Math.max(...Object.values(data).map(v => v.accuracy || 0), 1)
  const colors = { easy: 'var(--easy)', medium: 'var(--warning)', hard: 'var(--danger)', mcq: 'var(--accent)', true_false: 'var(--success)', fill_blank: 'var(--warning)' }

  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem' }}>
      <p style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{title}</p>
      {Object.entries(data).map(([key, val]) => (
        <div key={key} style={{ marginBottom: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{key.replace('_', ' ')}</span>
            <span style={{ fontSize: '0.82rem', fontWeight: '600', color: colors[key] || 'var(--accent)' }}>{val.accuracy}%</span>
          </div>
          <div style={{ height: '6px', background: 'var(--bg-hover)', borderRadius: '3px' }}>
            <div style={{ width: `${(val.accuracy / max) * 100}%`, height: '100%', background: colors[key] || 'var(--accent)', borderRadius: '3px', transition: 'width 0.6s ease' }} />
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>{val.correct}/{val.total} correct</p>
        </div>
      ))}
    </div>
  )
}

function Analytics({ onClose }) {
  const [stats, setStats] = useState(null)
  const [summary, setSummary] = useState(null)
  const [weakAreas, setWeakAreas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, summaryRes, weakRes] = await Promise.all([
          axios.get(`${API}/sessions/stats`),
          axios.get(`${API}/adaptive/summary`),
          axios.get(`${API}/adaptive/weak-areas`),
        ])
        setStats(statsRes.data)
        setSummary(summaryRes.data)
        setWeakAreas(weakRes.data.weak_areas || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>Loading analytics...</div>
  )

  return (
    <div style={{ marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '800' }}>📊 Analytics Dashboard</h2>
        <button onClick={onClose} style={{ padding: '6px 16px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.85rem' }}>← Back</button>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '1.5rem' }}>
        <StatCard label="Total Quizzes" value={stats?.total_quizzes || 0} color="var(--accent)" />
        <StatCard label="Avg Score" value={stats?.average_score || 0} color="var(--success)" suffix="%" />
        <StatCard label="Best Score" value={stats?.best_score || 0} color="var(--warning)" suffix="%" />
        <StatCard label="Questions Done" value={stats?.total_questions_attempted || 0} color="var(--danger)" />
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '1.5rem' }}>
        {summary?.by_difficulty && Object.keys(summary.by_difficulty).length > 0 && (
          <BarChart data={summary.by_difficulty} title="Accuracy by Difficulty" />
        )}
        {summary?.by_type && Object.keys(summary.by_type).length > 0 && (
          <BarChart data={summary.by_type} title="Accuracy by Question Type" />
        )}
      </div>

      {/* Grade Distribution */}
      {stats?.grade_distribution && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem', marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Grade Distribution</p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            {Object.entries(stats.grade_distribution).map(([grade, count]) => (
              <div key={grade} style={{ textAlign: 'center', padding: '0.8rem 1.2rem', background: 'var(--bg-secondary)', borderRadius: '10px', minWidth: '60px' }}>
                <p style={{ fontSize: '1.5rem', fontWeight: '700', color: grade === 'A' ? 'var(--success)' : grade === 'B' ? 'var(--warning)' : grade === 'F' ? 'var(--danger)' : 'var(--text-primary)' }}>{grade}</p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weak Areas */}
      {weakAreas.length > 0 && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid rgba(248,113,113,0.3)', borderRadius: '14px', padding: '1.2rem' }}>
          <p style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--danger)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>⚠ Areas to Improve</p>
          {weakAreas.map((area, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0', borderBottom: i < weakAreas.length - 1 ? '1px solid var(--border)' : 'none' }}>
              <div>
                <p style={{ fontSize: '0.85rem', fontWeight: '500' }}>{area.area}</p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{area.suggestion}</p>
              </div>
              <span style={{ padding: '2px 10px', borderRadius: '20px', background: 'rgba(248,113,113,0.1)', color: 'var(--danger)', fontSize: '0.8rem', fontWeight: '600' }}>{area.accuracy}%</span>
            </div>
          ))}
        </div>
      )}

      {weakAreas.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--success)', background: 'rgba(74,222,128,0.05)', borderRadius: '14px', border: '1px solid rgba(74,222,128,0.2)' }}>
          <p style={{ fontSize: '1.2rem', fontWeight: '600' }}>🎉 No weak areas detected!</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Keep up the great work!</p>
        </div>
      )}
    </div>
  )
}

export default Analytics
