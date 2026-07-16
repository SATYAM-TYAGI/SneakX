import React from 'react'

/**
 * Advanced Filters panel containing Brand, Type, Gender, Material, Color, and Maximum Budget.
 */
function Filters({ filters, setFilters, filterOptions, loading }) {
  // helper to update a single filter setting
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  // extract unique metadata lists from backend options, with fallback defaults
  const brands = filterOptions?.brands || []
  const types = filterOptions?.types || []
  const materials = filterOptions?.materials || []
  const colors = filterOptions?.colors || []


  return (
    <div className="filters-container">
      {/* Brand Selector */}
      <div className="filter-group">
        <label className="filter-label">Brand</label>
        <select
          className="filter-select"
          value={filters.brand}
          onChange={(e) => handleFilterChange('brand', e.target.value)}
          disabled={loading}
        >
          <option value="">All Brands</option>
          {brands.map(brand => (
            <option key={brand} value={brand}>{brand}</option>
          ))}
        </select>
      </div>

      {/* Type Selector */}
      <div className="filter-group">
        <label className="filter-label">Type</label>
        <select
          className="filter-select"
          value={filters.type}
          onChange={(e) => handleFilterChange('type', e.target.value)}
          disabled={loading}
        >
          <option value="">All Types</option>
          {types.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* Gender Selector */}
      <div className="filter-group">
        <label className="filter-label">Gender</label>
        <select
          className="filter-select"
          value={filters.gender}
          onChange={(e) => handleFilterChange('gender', e.target.value)}
          disabled={loading}
        >
          <option value="">All</option>
          <option value="men">Men</option>
          <option value="women">Women</option>
          <option value="unisex">Unisex</option>
          <option value="kids">Kids</option>
        </select>
      </div>

      {/* Color Selector */}
      <div className="filter-group">
        <label className="filter-label">Color</label>
        <select
          className="filter-select"
          value={filters.color || ''}
          onChange={(e) => handleFilterChange('color', e.target.value)}
          disabled={loading}
        >
          <option value="">All Colors</option>
          {colors.map(color => (
            <option key={color} value={color}>{color}</option>
          ))}
        </select>
      </div>


    </div>
  )
}

export default Filters
