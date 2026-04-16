import React, { useEffect, useState } from 'react'
import { getRecipe } from '../api/recipeApi'
import RecipeDetail from './RecipeDetail'

/** Modal wrapper that loads + displays full recipe detail by ID. */
export default function RecipeModal({ recipeId, onClose }) {
  const [recipe, setRecipe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    getRecipe(recipeId)
      .then(setRecipe)
      .catch(() => setError('Failed to load recipe details.'))
      .finally(() => setLoading(false))
  }, [recipeId])

  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div className="modal-header">
          <span className="modal-header-title">
            {recipe ? recipe.title : 'Recipe Details'}
          </span>
          <button className="modal-close" onClick={onClose} title="Close">✕</button>
        </div>
        <div className="modal-body">
          {loading && (
            <div className="loading-wrapper">
              <div className="spinner" />
              <span>Loading recipe…</span>
            </div>
          )}
          {error && <div className="error-box">{error}</div>}
          {!loading && !error && <RecipeDetail recipe={recipe} />}
        </div>
      </div>
    </div>
  )
}
