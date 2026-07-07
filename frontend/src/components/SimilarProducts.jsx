import React from 'react'

/**
 * Grid rendering smaller cards of similar sneakers.
 * Clicking a similar shoe replaces the modal's detail card view locally.
 */
function SimilarProducts({ products, onSelectShoe }) {
  return (
    <div className="similar-grid">
      {products.map((shoe) => (
        <div
          key={shoe.product_id}
          className="similar-card"
          onClick={() => onSelectShoe(shoe)}
        >
          {/* Card Image */}
          <div className="similar-card-img-wrapper">
            {shoe.thumbnail_url ? (
              <img
                src={shoe.thumbnail_url}
                alt={shoe.display_name}
                className="similar-card-img"
              />
            ) : (
              <div className="similar-card-placeholder">👟</div>
            )}
          </div>

          {/* Card Meta details */}
          <div className="similar-card-body">
            <span className="similar-card-brand">{shoe.brand}</span>
            <h4 className="similar-card-title">{shoe.display_name}</h4>
            <p className="similar-card-price">{shoe.retail_price}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default SimilarProducts
