import React from 'react'

/**
 * Single Recommendation card showing sneaker details.
 * Features a clean white background, soft shadow, and hover lift animation.
 */
function RecommendationCard({ shoe, onSelect }) {
  return (
    <div className="recommendation-card" onClick={onSelect}>
      {/* Product Image Wrapper */}
      <div className="card-image-wrapper">
        {shoe.thumbnail_url ? (
          <img src={shoe.thumbnail_url} alt={shoe.display_name} className="card-image" />
        ) : (
          <div className="card-image-placeholder">👟 No Image</div>
        )}
      </div>

      {/* Product Details Section */}
      <div className="card-info">
        <span className="card-brand">{shoe.brand}</span>
        <h3 className="card-title">{shoe.display_name}</h3>

        <div className="card-meta">
          <span className="card-type-tag">{shoe.type}</span>
          <span className="card-gender-tag">{shoe.gender}</span>
        </div>

        <p className="card-price">{shoe.retail_price}</p>

        <button className="card-action-btn" onClick={(e) => { e.stopPropagation(); onSelect(); }}>
          View Details
        </button>
      </div>
    </div>
  )
}

export default RecommendationCard
