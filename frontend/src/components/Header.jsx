import { BarChart2 } from 'lucide-react'

function Header({ onAnalytics, showAnalytics }) {
  return (
    <header style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-secondary)', padding: '1rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 100 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', fontWeight: '700', fontFamily: 'Syne, sans-serif' }}>C</div>
        <div>
          <h1 style={{ fontSize: '1.2rem', fontWeight: '700', letterSpacing: '-0.5px' }}>Cognify</h1>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '-2px' }}>AI Quiz Generator</p>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button onClick={onAnalytics} style={{ padding: '7px 16px', borderRadius: '8px', border: `1px solid ${showAnalytics ? 'var(--accent)' : 'var(--border)'}`, background: showAnalytics ? 'var(--accent-glow)' : 'transparent', color: showAnalytics ? 'var(--accent-light)' : 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', cursor: 'pointer', fontWeight: '500' }}>
          <BarChart2 size={14} /> Analytics
        </button>
        <span style={{ padding: '4px 12px', borderRadius: '20px', background: 'var(--accent-glow)', border: '1px solid var(--accent)', color: 'var(--accent-light)', fontSize: '0.75rem', fontWeight: '500' }}>v1.0.0</span>
      </div>
    </header>
  )
}

export default Header
