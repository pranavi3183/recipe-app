import React from 'react'

/** Renders the full recipe detail in a card-based layout.
 *  Used in both Tab 1 (after extraction) and the History modal. */
export default function RecipeDetail({ recipe }) {
  if (!recipe) return null

  const diff = recipe.difficulty?.toLowerCase() || 'easy'

  return (
    <div>
      {/* ── Hero ── */}
      <div className="recipe-hero">
        <div className="recipe-hero-title">{recipe.title || 'Untitled Recipe'}</div>
        <div className="recipe-meta-row">
          {recipe.cuisine && (
            <span className="meta-chip">
              🍽 <span className="value">{recipe.cuisine}</span>
            </span>
          )}
          {recipe.prep_time && (
            <span className="meta-chip">
              <span className="label">Prep</span>
              <span className="value">{recipe.prep_time}</span>
            </span>
          )}
          {recipe.cook_time && (
            <span className="meta-chip">
              <span className="label">Cook</span>
              <span className="value">{recipe.cook_time}</span>
            </span>
          )}
          {recipe.total_time && (
            <span className="meta-chip">
              <span className="label">Total</span>
              <span className="value">{recipe.total_time}</span>
            </span>
          )}
          {recipe.servings && (
            <span className="meta-chip">
              👤 <span className="value">{recipe.servings} servings</span>
            </span>
          )}
          {recipe.difficulty && (
            <span className={`difficulty-badge difficulty-${diff}`}>
              {recipe.difficulty}
            </span>
          )}
        </div>
      </div>

      {/* ── Nutrition ── */}
      {recipe.nutrition_estimate && Object.keys(recipe.nutrition_estimate).length > 0 && (
        <div className="card">
          <div className="card-title">📊 Nutrition Estimate <small style={{ color: 'var(--text-muted)', fontSize: '11px', textTransform: 'none', letterSpacing: 0 }}>(per serving)</small></div>
          <div className="nutrition-grid">
            {recipe.nutrition_estimate.calories != null && (
              <div className="nutrition-stat">
                <span className="nutrition-value">{recipe.nutrition_estimate.calories}</span>
                <span className="nutrition-label">Calories</span>
              </div>
            )}
            {recipe.nutrition_estimate.protein && (
              <div className="nutrition-stat">
                <span className="nutrition-value">{recipe.nutrition_estimate.protein}</span>
                <span className="nutrition-label">Protein</span>
              </div>
            )}
            {recipe.nutrition_estimate.carbs && (
              <div className="nutrition-stat">
                <span className="nutrition-value">{recipe.nutrition_estimate.carbs}</span>
                <span className="nutrition-label">Carbs</span>
              </div>
            )}
            {recipe.nutrition_estimate.fat && (
              <div className="nutrition-stat">
                <span className="nutrition-value">{recipe.nutrition_estimate.fat}</span>
                <span className="nutrition-label">Fat</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Ingredients + Instructions ── */}
      <div className="two-col">
        {recipe.ingredients && recipe.ingredients.length > 0 && (
          <div className="card">
            <div className="card-title">🧂 Ingredients</div>
            <ul className="ingredient-list">
              {recipe.ingredients.map((ing, i) => (
                <li key={i} className="ingredient-item">
                  <span className="ingredient-qty">{ing.quantity}</span>
                  <span className="ingredient-unit">{ing.unit}</span>
                  <span className="ingredient-name">{ing.item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {recipe.instructions && recipe.instructions.length > 0 && (
          <div className="card">
            <div className="card-title">📋 Instructions</div>
            <ol className="instructions-list">
              {recipe.instructions.map((step, i) => (
                <li key={i} className="instruction-item">
                  <span className="step-num">{i + 1}</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {/* ── Substitutions ── */}
      {recipe.substitutions && recipe.substitutions.length > 0 && (
        <div className="card">
          <div className="card-title">🔄 Ingredient Substitutions</div>
          <ul className="substitution-list">
            {recipe.substitutions.map((sub, i) => (
              <li key={i} className="substitution-item">
                <span className="sub-icon">✓</span>
                <span>{sub}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Shopping List + Related ── */}
      <div className="two-col">
        {recipe.shopping_list && Object.keys(recipe.shopping_list).length > 0 && (
          <div className="card">
            <div className="card-title">🛒 Shopping List</div>
            {Object.entries(recipe.shopping_list).map(([cat, items]) =>
              items && items.length > 0 ? (
                <div className="shopping-category" key={cat}>
                  <div className="shopping-category-title">{cat}</div>
                  <div className="shopping-items">
                    {items.map((item, i) => (
                      <span key={i} className="shopping-tag">{item}</span>
                    ))}
                  </div>
                </div>
              ) : null
            )}
          </div>
        )}

        {recipe.related_recipes && recipe.related_recipes.length > 0 && (
          <div className="card">
            <div className="card-title">💡 Related Recipes</div>
            <div className="related-list">
              {recipe.related_recipes.map((name, i) => (
                <div key={i} className="related-item">
                  <span className="related-dot">·</span>
                  {name}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── Source URL ── */}
      <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-muted)' }}>
        Source: <a href={recipe.url} target="_blank" rel="noreferrer"
          style={{ color: 'var(--accent-dim)', wordBreak: 'break-all' }}>{recipe.url}</a>
      </div>
    </div>
  )
}
