import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

/** POST /api/extract — scrape + extract recipe from URL */
export const extractRecipe = (url) =>
  api.post('/extract', { url }).then((r) => r.data)

/** GET /api/recipes — list all saved recipes */
export const listRecipes = () =>
  api.get('/recipes').then((r) => r.data)

/** GET /api/recipes/:id — full recipe detail */
export const getRecipe = (id) =>
  api.get(`/recipes/${id}`).then((r) => r.data)

/** DELETE /api/recipes/:id */
export const deleteRecipe = (id) =>
  api.delete(`/recipes/${id}`)

/** POST /api/meal-plan — generate merged shopping list */
export const generateMealPlan = (recipeIds) =>
  api.post('/meal-plan', { recipe_ids: recipeIds }).then((r) => r.data)
