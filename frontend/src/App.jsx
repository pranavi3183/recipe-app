import React, { useState } from 'react'
import ExtractTab from './pages/ExtractTab'
import HistoryTab from './pages/HistoryTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('extract')

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="app-header">
        <span className="app-logo">🍴</span>
        <h1 className="app-title">
          Recipe <span>Extractor</span> &amp; Meal Planner
        </h1>
      </header>

      {/* Tab Bar */}
      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'extract' ? 'active' : ''}`}
          onClick={() => setActiveTab('extract')}
        >
          🔍 Extract Recipe
        </button>
        <button
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📚 Saved Recipes
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'extract' ? <ExtractTab /> : <HistoryTab />}
    </div>
  )
}
