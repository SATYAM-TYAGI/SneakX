/**
 * API Service for SneakX Frontend
 * Handles recommendations and metadata filters API requests.
 */

/**
 * Fetch list of unique filter options from the backend.
 */
export async function getFilterMetadata() {
  const response = await fetch('/api/filters')
  if (!response.ok) {
    throw new Error("Could not fetch filter options from backend")
  }
  return response.json()
}

/**
 * Fetch recommendation list and similar products from the backend.
 */
export async function getRecommendations(query, filters) {
  const response = await fetch('/api/recommend', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      filters: {
        brand: filters.brand || null,
        type: filters.type || null,
        gender: filters.gender || null,
        material: filters.material || null,
        color: filters.color || null
      }
    })
  })

  if (!response.ok) {
    throw new Error("Server responded with error status.")
  }

  return response.json()
}

/**
 * Fetch similar products dynamically for a sneaker by its product ID.
 */
export async function getSimilarProducts(productId) {
  const response = await fetch(`/api/similar/${productId}`)
  if (!response.ok) {
    throw new Error("Could not fetch similar products for sneaker")
  }
  return response.json()
}
