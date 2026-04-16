import React, { useState } from 'react'
import { extractRecipe } from '../api/recipeApi'
import RecipeDetail from '../components/RecipeDetail'

export default function ExtractTab() {
  const [url, setUrl] = useState('')
  const [recipe, setRecipe] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleExtract = async () => {
    const trimmed = url.trim()
    if (!trimmed) return

    if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
      setError('Please enter a valid URL starting with http:// or https://')
      return
    }

    setLoading(true)
    setError('')
    setRecipe(null)

    try {
      const data = await extractRecipe(trimmed)
      setRecipe(data)
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(
        typeof detail === 'string'
          ? detail
          : 'Failed to extract recipe. Check the URL and try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleExtract()
  }

  return (
    <div>
      {/* URL Input */}
      <div className="extract-section">
        <label className="input-label">Recipe Blog URL</label>
        <div className="url-input-row">
          <input
            className="url-input"
            type="url"
            placeholder="https://www.allrecipes.com/recipe/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={handleExtract}
            disabled={loading || !url.trim()}
          >
            {loading ? (
              <>
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                Extracting…
              </>
            ) : (
              <>🔍 Extract Recipe</>
            )}
          </button>
        </div>

        {error && <div className="error-box">{error}</div>}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="loading-wrapper">
          <div className="spinner" />
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontWeight: 500, marginBottom: 6 }}>Scraping & Analyzing…</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Fetching page → Sending to Gemini → Extracting structured data
            </div>
          </div>
        </div>
      )}

      {/* Result */}
      {!loading && recipe && (
        <div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10,
            marginBottom: 20, padding: '10px 16px',
            background: 'rgba(109,189,138,0.08)',
            border: '1px solid rgba(109,189,138,0.2)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 14, color: 'var(--green)'
          }}>
            ✓ Recipe extracted and saved successfully
          </div>
          <RecipeDetail recipe={recipe} />
        </div>
      )}

      {/* Empty state */}
      {!loading && !recipe && !error && (
        <div className="empty-state">
          <div className="icon">🍳</div>
          <p>Paste a recipe blog URL above and click <strong>Extract Recipe</strong></p>
          <p style={{ marginTop: 8, fontSize: 13 }}>Works with AllRecipes, BBC Good Food, Simply Recipes, and more</p>
        </div>
      )}
    </div>
  )
}
