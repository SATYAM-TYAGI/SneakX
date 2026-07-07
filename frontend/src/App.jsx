import React, { useState, useEffect, useRef } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom'
import SearchBar from './components/SearchBar.jsx'
import Filters from './components/Filters.jsx'
import TopRecommendations from './components/TopRecommendations.jsx'
import ProductDetails from './pages/ProductDetails.jsx'
import LoadingSpinner from './components/LoadingSpinner.jsx'
import { getFilterMetadata, getRecommendations } from './services/api'

/**
 * Search Dashboard Home page component.
 * Renders search bar, advanced filter panels, and search results lists.
 */
function Home({
  query,
  setQuery,
  filters,
  setFilters,
  loading,
  setLoading,
  hasSearched,
  setHasSearched,
  error,
  setError,
  recommendations,
  setRecommendations,
  similarProducts,
  setSimilarProducts,
  filterOptions,
  setFilterOptions,
  handleSearch,
  resultsRef
}) {
  const navigate = useNavigate()

  // handler to navigate to product details route
  const handleSelectShoe = (shoe) => {
    navigate(`/product/${shoe.product_id}`, {
      state: {
        product: shoe,
        recommendations: recommendations,
        similarProducts: similarProducts
      }
    })
  }

  return (
    <main className="app-content">
      <section className="hero-section">
        <h1 className="hero-title">Find Your Next <span>Sneakers</span></h1>
        <p className="hero-description">
          Discover, Search, and get smart recommendations.
        </p>
      </section>

      <section className="search-section">
        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={handleSearch}
          loading={loading}
        />
        <Filters
          filters={filters}
          setFilters={setFilters}
          filterOptions={filterOptions}
          loading={loading}
        />
        <button
          className="find-sneakers-btn"
          onClick={handleSearch}
          disabled={loading}
        >
          {loading ? "Searching..." : "Find Sneakers"}
        </button>
      </section>

      {/* Results Panel */}
      <section ref={resultsRef} className="results-container">
        {loading && <LoadingSpinner />}

        {!loading && error && (
          <div className="status-message error-message">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && hasSearched && recommendations.length === 0 && (
          <div className="status-message empty-message">
            <h3>No Sneakers Found</h3>
            <p>No sneakers matched your search. Try changing your filters.</p>
          </div>
        )}

        {!loading && !error && recommendations.length > 0 && (
          <div className="results-wrapper">
            <h2 className="section-title">Recommended For You</h2>
            <TopRecommendations
              recommendations={recommendations}
              onSelectShoe={handleSelectShoe}
            />
          </div>
        )}
      </section>
    </main>
  )
}

/**
 * AppContent wraps components inside BrowserRouter context.
 * Manages search/recommendation states to preserve state across page transitions.
 */
function AppContent() {
  // main search query state
  const [query, setQuery] = useState('')

  // filters selections state
  const [filters, setFilters] = useState({
    brand: '',
    type: '',
    gender: '',
    material: '',
    color: ''
  })

  // runtime status states
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [error, setError] = useState(null)

  // result sets states
  const [recommendations, setRecommendations] = useState([])
  const [similarProducts, setSimilarProducts] = useState([])

  // dynamic filter select lists from backend
  const [filterOptions, setFilterOptions] = useState({
    brands: [],
    types: [],
    materials: [],
    colors: []
  })

  // reference point for scrolling down to results section
  const resultsRef = useRef(null)

  // fetch dynamic options lists from backend metadata
  useEffect(() => {
    const fetchFilterMetadata = async () => {
      try {
        const data = await getFilterMetadata()
        setFilterOptions(data)
        // default filters setup
      } catch (err) {
        console.error("Could not fetch filter options from backend:", err)
        // fallback defaults if server fails
        setFilterOptions({
          brands: ['Nike', 'adidas', 'Jordan', 'New Balance', 'Vans', 'Puma', 'Converse', 'Reebok', 'ASICS'],
          types: ['Running', 'Basketball', 'Casual', 'Lifestyle', 'Skate', 'Fashion'],
          materials: ['Leather', 'Mesh', 'Suede', 'Canvas', 'Primeknit'],
          colors: ['Black', 'White', 'Grey', 'Red', 'Blue', 'Green'],
        })
      }
    }

    fetchFilterMetadata()
  }, [])

  // handler to fetch search recommendations
  const handleSearch = async () => {
    setLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      const data = await getRecommendations(query, filters)

      setRecommendations(data.recommendations || [])
      setSimilarProducts(data.similar_products || [])

      // smooth scroll to results section
      setTimeout(() => {
        if (resultsRef.current) {
          resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)

    } catch (err) {
      console.error("API connection failed:", err)
      setError("Unable to connect to the recommendation service. Please try again.")
      setRecommendations([])
      setSimilarProducts([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      {/* Upper Title Area */}
      <header className="app-header">
        <div className="logo-container">
          <Link to="/" className="logo-link">
            <span className="logo-text">Sneaks<span className="logo-highlight">X</span></span>
            <span className="logo-badge">Recommendation Portal</span>
          </Link>
        </div>
        <p className="app-subtitle">Discover Your Next Sneakers</p>
      </header>

      {/* Route mapping */}
      <Routes>
        <Route
          path="/"
          element={
            <Home
              query={query}
              setQuery={setQuery}
              filters={filters}
              setFilters={setFilters}
              loading={loading}
              setLoading={setLoading}
              hasSearched={hasSearched}
              setHasSearched={setHasSearched}
              error={error}
              setError={setError}
              recommendations={recommendations}
              setRecommendations={setRecommendations}
              similarProducts={similarProducts}
              setSimilarProducts={setSimilarProducts}
              filterOptions={filterOptions}
              setFilterOptions={setFilterOptions}
              handleSearch={handleSearch}
              resultsRef={resultsRef}
            />
          }
        />
        <Route path="/product/:id" element={<ProductDetails />} />
      </Routes>

      {/* Bottom Footer Area */}
      <footer className="app-footer">
        <p>SneakX © 2026 • Designed by Satyam Tyagi</p>
      </footer>
    </div>
  )
}

/**
 * Main application router manager.
 */
function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}

export default App
