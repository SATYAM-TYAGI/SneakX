import React from 'react'
import RecommendationCard from './RecommendationCard.jsx'

/**
 * Grid rendering for the Top 5 recommended shoes.
 */
function TopRecommendations({ recommendations, onSelectShoe }) {
  // limit recommendations to top 5 items
  const topFive = recommendations.slice(0, 5)

  return (
    <div className="recommendations-grid">
      {topFive.map((shoe) => (
        <RecommendationCard
          key={shoe.product_id}
          shoe={shoe}
          onSelect={() => onSelectShoe(shoe)}
        />
      ))}
    </div>
  )
}

export default TopRecommendations
