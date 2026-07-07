import React from 'react'

/**
 * SearchBar component for typing natural language queries.
 */
function SearchBar({ query, setQuery, onSearch, loading }) {
  // handle pressing the Enter key to start search
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !loading) {
      onSearch()
    }
  }

  return (
    <div className="search-bar-container">
      <input
        type="text"
        className="search-input"
        placeholder='e.g., "comfortable white running shoes"'
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />
    </div>
  )
}

export default SearchBar
