import React, { useState, useEffect, useCallback } from 'react'
import { listRecipes, deleteRecipe, generateMealPlan } from '../api/recipeApi'
import RecipeModal from '../components/RecipeModal'
import MealPlanModal from '../components/MealPlanModal'

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

export default function HistoryTab() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Modal state
  const [detailId, setDetailId] = useState(null)

  // Meal plan selection
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [planLoading, setPlanLoading] = useState(false)
  const [planError, setPlanError] = useState('')
  const [mealPlan, setMealPlan] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    listRecipes()
      .then(setRecipes)
      .catch(() => setError('Failed to load recipe history.'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this recipe from history?')) return
    try {
      await deleteRecipe(id)
      setRecipes((prev) => prev.filter((r) => r.id !== id))
      setSelectedIds((prev) => { const s = new Set(prev); s.delete(id); return s })
    } catch {
      alert('Failed to delete recipe.')
    }
  }

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      const s = new Set(prev)
      s.has(id) ? s.delete(id) : s.add(id)
      return s
    })
  }

  const handleGeneratePlan = async () => {
    if (selectedIds.size < 2) return
    setPlanLoading(true)
    setPlanError('')
    try {
      const plan = await generateMealPlan([...selectedIds])
      setMealPlan(plan)
    } catch (err) {
      const detail = err?.response?.data?.detail
      setPlanError(typeof detail === 'string' ? detail : 'Failed to generate meal plan.')
    } finally {
      setPlanLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-wrapper">
        <div className="spinner" />
        <span>Loading history…</span>
      </div>
    )
  }

  if (error) return <div className="error-box">{error}</div>

  if (recipes.length === 0) {
    return (
      <div className="empty-state">
        <div className="icon">📚</div>
        <p>No recipes saved yet.</p>
        <p style={{ marginTop: 8, fontSize: 13 }}>Extract your first recipe from Tab 1!</p>
      </div>
    )
  }

  return (
    <div>
      {/* Meal Plan Bar */}
      {selectedIds.size > 0 && (
        <div className="meal-plan-bar">
          <span className="info">
            <strong>{selectedIds.size}</strong> recipe{selectedIds.size > 1 ? 's' : ''} selected
            {selectedIds.size < 2 && ' — select at least 2 to generate a meal plan'}
          </span>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            {planError && <span style={{ fontSize: 13, color: 'var(--red)' }}>{planError}</span>}
            <button className="btn btn-ghost" onClick={() => setSelectedIds(new Set())}>
              Clear
            </button>
            <button
              className="btn btn-primary"
              disabled={selectedIds.size < 2 || planLoading}
              onClick={handleGeneratePlan}
            >
              {planLoading ? (
                <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Generating…</>
              ) : (
                '🥗 Generate Meal Plan'
              )}
            </button>
          </div>
        </div>
      )}

      {/* History Table */}
      <div className="history-table-wrap">
        <table className="history-table">
          <thead>
            <tr>
              <th style={{ width: 40 }}>
                <input
                  type="checkbox"
                  onChange={(e) => {
                    if (e.target.checked) setSelectedIds(new Set(recipes.map((r) => r.id)))
                    else setSelectedIds(new Set())
                  }}
                  checked={selectedIds.size === recipes.length && recipes.length > 0}
                  title="Select all"
                  style={{ accentColor: 'var(--accent)', cursor: 'pointer' }}
                />
              </th>
              <th>Title</th>
              <th>Cuisine</th>
              <th>Difficulty</th>
              <th>Extracted</th>
              <th>URL</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recipes.map((r) => (
              <tr key={r.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedIds.has(r.id)}
                    onChange={() => toggleSelect(r.id)}
                    style={{ accentColor: 'var(--accent)', cursor: 'pointer' }}
                  />
                </td>
                <td className="title-cell">{r.title || '—'}</td>
                <td>{r.cuisine || '—'}</td>
                <td>
                  {r.difficulty ? (
                    <span className={`difficulty-badge difficulty-${r.difficulty.toLowerCase()}`}>
                      {r.difficulty}
                    </span>
                  ) : '—'}
                </td>
                <td>{formatDate(r.created_at)}</td>
                <td className="url-cell" title={r.url}>{r.url}</td>
                <td>
                  <div className="td-actions">
                    <button className="btn btn-ghost" onClick={() => setDetailId(r.id)}>
                      Details
                    </button>
                    <button className="btn btn-danger" onClick={(e) => handleDelete(r.id, e)}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {detailId && (
        <RecipeModal recipeId={detailId} onClose={() => setDetailId(null)} />
      )}

      {/* Meal Plan Modal */}
      {mealPlan && (
        <MealPlanModal plan={mealPlan} onClose={() => setMealPlan(null)} />
      )}
    </div>
  )
}
