import React from 'react';
import {
  ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Bar, Cell,
  PieChart, Pie, Legend, AreaChart, Area
} from 'recharts';

export default function AnalyticsCharts({
  movieTitle,
  ratingComparisonData,
  sentimentPieData,
  aspectData,
  integrity,
  emotionMetrics,
  positivityTrendData
}) {
  return (
    <div className="analytics-section fade-in">
      <div style={{ marginBottom: '24px' }}>
        <h2 className="movie-detail-title" style={{ fontSize: '24px', marginBottom: '6px' }}>
          Visual Analytics: <span className="accent-gradient">{movieTitle}</span>
        </h2>
        <p style={{ color: 'hsl(var(--text-muted))', fontSize: '12.5px' }}>
          Interactive charts aggregating sentiment distributions, dynamic aspect polarity, and review pool authenticity models.
        </p>
      </div>

      {/* Grid Visual Charts */}
      <div className="analytics-charts-grid">
        
        {/* Rating comparison */}
        <div className="chart-card glass-panel">
          <h4 className="chart-card-title text-gradient">Score Comparisons</h4>
          <p className="chart-card-desc">Normalized scores out of 10 comparing primary catalog providers.</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ratingComparisonData} margin={{ top: 20, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
                <Bar dataKey="Score" radius={[4, 4, 0, 0]}>
                  {ratingComparisonData.map((entry, index) => {
                    const colors = ['#fbbf24', 'hsl(var(--accent-secondary))', '#f87171', '#4ade80', 'hsl(var(--accent-primary))'];
                    return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sentiment Pie */}
        <div className="chart-card glass-panel">
          <h4 className="chart-card-title text-gradient">Vibe Distribution</h4>
          <p className="chart-card-desc">Volume of positive, negative, and neutral review classifications.</p>
          <div className="chart-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {sentimentPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
                  <Legend verticalAlign="bottom" height={36} tick={{ fill: 'hsl(var(--text-main))', fontSize: 10 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ color: 'hsl(var(--text-muted))', fontSize: '12px' }}>Scrape feedback to compile sentiment ratio pie.</div>
            )}
          </div>
        </div>

        {/* Aspect Based (ABSA) aspect scores */}
        <div className="chart-card glass-panel">
          <h4 className="chart-card-title text-gradient">Aspect breakdowns (ABSA)</h4>
          <p className="chart-card-desc">Average sentiment ratings across key aesthetic film vectors.</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aspectData} layout="vertical" margin={{ top: 15, right: 10, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" tick={{ fill: 'hsl(var(--text-main))', fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
                <Bar dataKey="Score" radius={[0, 4, 4, 0]} barSize={12}>
                  {aspectData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Integrity Audit circular shield card */}
        <div className="chart-card glass-panel" style={{ justifyContent: 'space-between' }}>
          <div>
            <h4 className="chart-card-title text-gradient">Pool Authenticity Shield</h4>
            <p className="chart-card-desc">Credibility metrics evaluating duplicated text and automation flags.</p>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexGrow: 1, padding: '10px 0' }}>
            <div className="integrity-score-ring" style={{ width: '90px', height: '90px', flexShrink: 0, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="100%" height="100%" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="rgba(255,255,255,0.03)" strokeWidth="8" />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  stroke={integrity.integrity_score > 85 ? '#22c55e' : (integrity.integrity_score > 60 ? '#fbbf24' : '#ef4444')}
                  strokeWidth="8"
                  strokeDasharray={2 * Math.PI * 40}
                  strokeDashoffset={2 * Math.PI * 40 * (1 - integrity.integrity_score / 100.0)}
                  strokeLinecap="round"
                />
              </svg>
              <div style={{ position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '18px', fontWeight: '800', color: 'hsl(var(--text-main))' }}>{integrity.integrity_score}%</span>
                <span style={{ fontSize: '6.5px', color: 'hsl(var(--text-muted))', letterSpacing: '0.05em', fontWeight: 'bold' }}>CREDIBILITY</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flexGrow: 1, fontSize: '11px', fontFamily: 'monospace' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed hsla(var(--text-main)/0.06)', paddingBottom: '4px' }}>
                <span style={{ color: 'hsl(var(--text-muted))' }}>Authenticity Rank:</span>
                <span style={{ fontWeight: 'bold', color: integrity.integrity_score > 85 ? '#4ade80' : '#fbbf24' }}>
                  {integrity.integrity_score > 85 ? 'SECURED' : 'CHECKED'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed hsla(var(--text-main)/0.06)', paddingBottom: '4px' }}>
                <span style={{ color: 'hsl(var(--text-muted))' }}>Spam Flagged:</span>
                <span style={{ fontWeight: 'bold', color: integrity.spam_count > 0 ? '#fbbf24' : 'hsl(var(--text-muted))' }}>
                  {integrity.spam_count}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed hsla(var(--text-main)/0.06)', paddingBottom: '4px' }}>
                <span style={{ color: 'hsl(var(--text-muted))' }}>Automation Triggers:</span>
                <span style={{ fontWeight: 'bold', color: integrity.bot_flag_count > 0 ? '#ef4444' : 'hsl(var(--text-muted))' }}>
                  {integrity.bot_flag_count}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'hsl(var(--text-muted))' }}>Duplicate Posts:</span>
                <span style={{ fontWeight: 'bold', color: integrity.duplicate_count > 0 ? '#fbbf24' : 'hsl(var(--text-muted))' }}>
                  {integrity.duplicate_count}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Audience Mood Bar Charts */}
        <div className="chart-card glass-panel">
          <h4 className="chart-card-title text-gradient">Audience Mood Gauge</h4>
          <p className="chart-card-desc">Calculated emotional signals detected in aggregated review texts.</p>
          <div className="mood-analysis-container">
            <div className="mood-bar-item">
              <div className="mood-bar-label-row">
                <span style={{ color: 'hsl(var(--text-main))' }}>Narrative Focus</span>
                <span style={{ color: '#a78bfa' }}>{emotionMetrics.narrative}%</span>
              </div>
              <div className="mood-bar-track">
                <div className="mood-bar-fill" style={{ width: `${emotionMetrics.narrative}%`, background: '#a78bfa' }}></div>
              </div>
            </div>
            <div className="mood-bar-item">
              <div className="mood-bar-label-row">
                <span style={{ color: 'hsl(var(--text-main))' }}>Cinema Joy & Excitement</span>
                <span style={{ color: '#22c55e' }}>{emotionMetrics.joy}%</span>
              </div>
              <div className="mood-bar-track">
                <div className="mood-bar-fill" style={{ width: `${emotionMetrics.joy}%`, background: '#22c55e' }}></div>
              </div>
            </div>
            <div className="mood-bar-item">
              <div className="mood-bar-label-row">
                <span style={{ color: 'hsl(var(--text-main))' }}>Surprise & Speculation</span>
                <span style={{ color: '#facc15' }}>{emotionMetrics.surprise}%</span>
              </div>
              <div className="mood-bar-track">
                <div className="mood-bar-fill" style={{ width: `${emotionMetrics.surprise}%`, background: '#facc15' }}></div>
              </div>
            </div>
            <div className="mood-bar-item">
              <div className="mood-bar-label-row">
                <span style={{ color: 'hsl(var(--text-main))' }}>Dramatic Tension</span>
                <span style={{ color: '#ef4444' }}>{emotionMetrics.tension}%</span>
              </div>
              <div className="mood-bar-track">
                <div className="mood-bar-fill" style={{ width: `${emotionMetrics.tension}%`, background: '#ef4444' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Positivity Area Timeline */}
        <div className="chart-card glass-panel">
          <h4 className="chart-card-title text-gradient">Chronological Sentiment Vibe</h4>
          <p className="chart-card-desc">Moving average of review sentiment ratings over the extracted review timeline.</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={positivityTrendData} margin={{ top: 20, right: 10, left: -25, bottom: 5 }}>
                <defs>
                  <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--accent-primary))" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="hsl(var(--accent-primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(var(--glass-bg), 0.95)', border: '1px solid hsla(var(--text-main) / 0.1)', borderRadius: '12px', color: 'hsl(var(--text-main))' }} />
                <Area type="monotone" dataKey="Vibe Score" stroke="hsl(var(--accent-primary))" strokeWidth={2} fillOpacity={1} fill="url(#trendGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
