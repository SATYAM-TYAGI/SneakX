import React from 'react'

/**
 * Loading Spinner shown in the center of the viewport during API requests.
 */
function LoadingSpinner() {
  return (
    <div className="spinner-container">
      <div className="spinner-ring"></div>
      <p className="spinner-text">Finding the best sneakers...</p>
    </div>
  )
}

export default LoadingSpinner
