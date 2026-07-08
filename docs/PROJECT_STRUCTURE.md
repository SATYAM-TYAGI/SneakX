# Project Structure

Here is how I organized the files in the SneakX project. I tried to keep this project structure clean and simple.

```
SneakX/
├── backend/
│   ├── data/
│   │   ├── Updated_Sneakers.csv         # Raw CSV shoe data
│   │   ├── processed_dataset.parquet   # Pandas processed dataset
│   │   ├── embeddings_*.npy             # Vector embeddings for semantic search
│   │   └── tfidf_*.pkl                 # TF-IDF vectors
│   ├── engine/
│   │   ├── recommendation_engine.py    # Similarity and diversity calculations
│   │   └── semantic_search.py          # Embedding generation helper
│   ├── main.py                          # FastAPI router and entry point
│   ├── requirements.txt                 # Python libraries list
│   └── Dockerfile                       # Docker instructions for the backend
├── frontend/
│   ├── public/                          # Public static files
│   ├── src/
│   │   ├── assets/                      # UI images and icons
│   │   ├── components/                  # UI components
│   │   │   ├── SearchBar.jsx
│   │   │   ├── Filters.jsx
│   │   │   ├── TopRecommendations.jsx
│   │   │   ├── SimilarProducts.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── pages/                       # Dedicated page components
│   │   │   └── ProductDetails.jsx       # Shoe detail specs page
│   │   ├── services/                    # API connection handlers
│   │   │   └── api.js                   # Functions for making backend requests
│   │   ├── App.jsx                      # App states and router setup
│   │   ├── main.jsx                     # Vite main React entry
│   │   └── index.css                    # Custom CSS styling
│   ├── package.json                     # Frontend scripts and node packages
│   ├── vite.config.js                   # Vite and proxy settings
│   └── Dockerfile                       # Docker instructions for frontend
├── docs/                                # Project documentation folder
├── screenshots/                         # Screenshots folder
├── README.md                            # High level overview page
├── docker-compose.yml                   # Docker orchestrator
└── .gitignore                           # Ignored git files
```
