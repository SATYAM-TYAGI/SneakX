# System Architecture

This document describes how the different components of SneakX talk to each other.

---

## Architecture Diagram

Here is a simple look at how data flows through the application:

```mermaid
graph TD
    subgraph Frontend Container (React)
        UI[App.jsx & UI Components]
        API_Call[services/api.js]
    end

    subgraph Backend Container (FastAPI)
        API[main.py API Gateway]
        Engine[engine/recommendation_engine.py]
        Data[engine/semantic_search.py]
        Files[(backend/data/ data files)]
    end

    UI -->|1. User Inputs| API_Call
    API_Call -->|2. Send Request| API
    API -->|3. Load Data| Files
    API -->|4. Get recommendations| Engine
    Engine -->|5. Compute similarity| Data
    API -->|6. Return JSON response| API_Call
    API_Call -->|7. Update React state| UI
```

---

## Description of the Modules

### 1. Frontend (React)
* I built the frontend using React and styled it using vanilla CSS.
* It is a clean dashboard with a search bar and dropdown filters.
* I used `services/api.js` to write the network fetch requests.
* When you click a shoe, it navigates to the `/product/:id` route using React Router.

### 2. Backend (FastAPI)
* I used FastAPI to run the backend web server.
* On startup, it loads the dataset parquet file and pre-computed embeddings (Identity and Description vectors only) into memory.
* It exposes the `/api/recommend`, `/api/filters`, and `/api/similar/{product_id}` endpoints for the frontend.

### 3. Recommendation Math (`backend/engine/`)
* **`recommendation_engine.py`**: Contains the code for hard filtering, Description + BM25 hybrid semantic searches, and trait-based Similar Products comparisons.
* **`semantic_search.py`**: Interacts with the Sentence Transformer model to calculate text embedding vectors.
* **`backend/data/`**: Stores the processed Parquet dataset, Identity & Description embeddings, and the BM25 index.
