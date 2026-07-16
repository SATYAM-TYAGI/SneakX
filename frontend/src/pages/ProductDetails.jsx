import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import SimilarProducts from '../components/SimilarProducts.jsx'
import { getSimilarProducts } from '../services/api.js'

/**
 * Dedicated Product Details page rendering detailed metrics of the selected sneaker
 * and a list of similar products at the bottom.
 */
function ProductDetails() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()

  // extract the state variables passed via React Router navigation
  const state = location.state || {}
  const currentProduct = state.product
  const recommendations = state.recommendations || []

  // local state to store similar products for the selected sneaker
  const [similarShoes, setSimilarShoes] = useState([])
  const [loadingSimilar, setLoadingSimilar] = useState(false)

  // scroll to top when active product changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [id])

  // fetch similar products dynamically from the backend API when the shoe ID changes
  useEffect(() => {
    if (currentProduct) {
      setLoadingSimilar(true)
      getSimilarProducts(currentProduct.product_id)
        .then((data) => {
          setSimilarShoes(data.similar_products || [])
        })
        .catch((err) => {
          console.error("Failed to load similar products:", err)
        })
        .finally(() => {
          setLoadingSimilar(false)
        })
    }
  }, [currentProduct?.product_id])

  // if the route was accessed directly, state is missing, so we guide them back
  if (!currentProduct) {
    return (
      <div className="product-details-container error-state-container">
        <h2>No Product Context Found</h2>
        <p>Please perform a search on the home dashboard first to load sneaker recommendations.</p>
        <Link to="/" className="back-home-btn">Go to Home Dashboard</Link>
      </div>
    )
  }

  // extract image properties
  const mainImage = currentProduct.thumbnail_url

  // filter out the current product from similar shoes grid
  const otherSimilarProducts = similarShoes.filter(
    (shoe) => shoe.product_id !== currentProduct.product_id
  )

  // handler to navigate locally to another similar product in-place
  const handleSelectSimilarProduct = (similarProduct) => {
    navigate(`/product/${similarProduct.product_id}`, {
      state: {
        product: similarProduct,
        recommendations
      }
    })
  }

  return (
    <div className="product-details-container">
      <div className="back-link-wrapper">
        <Link to="/" state={{ recommendations, similarProducts: similarShoes }} className="back-to-search-btn">
          ← Back to Search
        </Link>
      </div>

      <div className="product-details-card">
        <div className="product-details-grid">
          {/* Image Column */}
          <div className="details-image-section">
            <div className="details-main-image-wrapper">
              <img
                src={mainImage}
                alt={currentProduct.display_name}
                className="details-main-image"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://stockx-assets.imgix.net/media/Product-Placeholder-Default-20210415.jpg?fit=fill&bg=FFFFFF&w=700&h=500&fm=webp&auto=compress&q=90&dpr=2&trim=color';
                }}
              />
            </div>
          </div>

          {/* Details Specifications Column */}
          <div className="details-info-section">
            <div className="details-brand">{currentProduct.brand}</div>
            <h1 className="details-title">{currentProduct.display_name}</h1>
            <div className="details-price">Retail Price: <span className="price-tag">{currentProduct.retail_price}</span></div>

            <div className="specs-table">
              <div className="spec-row">
                <span className="spec-label">Model:</span>
                <span className="spec-value">{currentProduct.model}</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Type Category:</span>
                <span className="spec-value">{currentProduct.type}</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Gender:</span>
                <span className="spec-value">{currentProduct.gender}</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Colorway:</span>
                <span className="spec-value">{currentProduct.color}</span>
              </div>
              <div className="spec-row">
                <span className="spec-label">Materials:</span>
                <span className="spec-value">{currentProduct.material}</span>
              </div>
            </div>

            <div className="details-description-box">
              <h3>Description</h3>
              <p>{currentProduct.description}</p>
            </div>

            {currentProduct.stockx_url && (
              <a
                href={currentProduct.stockx_url}
                target="_blank"
                rel="noopener noreferrer"
                className="stockx-buy-btn"
              >
                View on StockX
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Similar products explore grid */}
      {otherSimilarProducts.length > 0 && (
        <div className="similar-products-section">
          <h2 className="similar-products-title">Check Out Similar Sneakers</h2>
          <SimilarProducts
            products={otherSimilarProducts}
            onSelectShoe={handleSelectSimilarProduct}
          />
        </div>
      )}
    </div>
  )
}

export default ProductDetails
