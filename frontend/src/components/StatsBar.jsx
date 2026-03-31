function StatsBar({ quiz }) {
  const stats = [
    { label: 'Total Questions', value: quiz.total_questions, color: 'var(--accent)' },
    { label: 'MCQ', value: quiz.breakdown?.mcq || 0, color: '#6c63ff' },
    { label: 'True / False', value: quiz.breakdown?.true_false || 0, color: '#4ade80' },
    { label: 'Fill in Blank', value: quiz.breakdown?.fill_blank || 0, color: '#fbbf24' },
  ]

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '12px',
      marginBottom: '2rem',
    }}>
      {stats.map((stat, i) => (
        <div key={i} style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: '14px',
          padding: '1.2rem',
          textAlign: 'center',
          borderTop: `3px solid ${stat.color}`,
        }}>
          <p style={{
            fontSize: '2rem',
            fontWeight: '700',
            fontFamily: 'Syne, sans-serif',
            color: stat.color,
            lineHeight: 1,
            marginBottom: '6px',
          }}>
            {stat.value}
          </p>
          <p style={{
            fontSize: '0.78rem',
            color: 'var(--text-secondary)',
            fontWeight: '500',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}>
            {stat.label}
          </p>
        </div>
      ))}
    </div>
  )
}

export default StatsBar