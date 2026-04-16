import React from 'react'

/** Displays the LLM-generated merged meal plan shopping list. */
export default function MealPlanModal({ plan, onClose }) {
  if (!plan) return null

  const categories = plan.merged_shopping_list || {}

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div className="modal-header">
          <span className="modal-header-title">🥗 {plan.plan_title || 'Meal Plan'}</span>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body meal-plan-result">

          {/* Recipes included */}
          {plan.recipes_included && plan.recipes_included.length > 0 && (
            <div className="card" style={{ marginBottom: 20 }}>
              <div className="card-title">📌 Recipes Included</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {plan.recipes_included.map((r, i) => (
                  <span key={i} className="shopping-tag" style={{ color: 'var(--text-primary)' }}>{r}</span>
                ))}
              </div>
              {plan.estimated_prep_time_total && (
                <div style={{ marginTop: 12, fontSize: 14, color: 'var(--text-secondary)' }}>
                  ⏱ Estimated total prep time: <strong style={{ color: 'var(--accent)' }}>{plan.estimated_prep_time_total}</strong>
                </div>
              )}
            </div>
          )}

          {/* Merged shopping list */}
          <div className="card">
            <div className="card-title">🛒 Merged Shopping List</div>
            {Object.entries(categories).map(([cat, items]) =>
              items && items.length > 0 ? (
                <div className="plan-category" key={cat}>
                  <div className="plan-category-title">{cat}</div>
                  {items.map((item, i) => (
                    <div key={i} className="plan-item-row">
                      <span className="plan-item-name">{item.item}</span>
                      <span className="plan-item-qty">{item.total_quantity}</span>
                    </div>
                  ))}
                </div>
              ) : null
            )}
          </div>

          {/* Tips */}
          {plan.tips && plan.tips.length > 0 && (
            <div className="card">
              <div className="card-title">💡 Meal Prep Tips</div>
              <ul className="tips-list">
                {plan.tips.map((tip, i) => (
                  <li key={i} className="tip-item">
                    <span style={{ color: 'var(--accent)' }}>→</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
