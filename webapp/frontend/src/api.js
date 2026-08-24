const BASE = ''

async function getJSON(url, options = {}) {
  const resp = await fetch(url, options)
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.json()
}

export function searchProducts({ q = '', category = '', limit = 20, signal } = {}) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (category) params.set('category', category)
  params.set('limit', String(limit))
  return getJSON(`${BASE}/search?${params.toString()}`, { signal })
}

export function compareProduct(id, { signal } = {}) {
  return getJSON(`${BASE}/products/${id}/compare`, { signal })
}

export function listCategories({ signal } = {}) {
  return getJSON(`${BASE}/categories`, { signal })
}