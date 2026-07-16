# SneakX - Sneaker Recommendation Platform

Welcome to SneakX! A great sneaker recommendation Platform. 

---

## What SneakX Does
Standard search boxes only match exact words. If you search for "runners," you might miss shoes that have "running" in the title or description. 
I built SneakX using semantic embeddings. It understands what you mean, matching the overall concept and details of your query.

---

## Features
* **Semantic Search**: Understands natural language queries (like *"comfortable running shoes"*).
* **Smart Filter Matching**: Automatically filters brands, types, materials, colors, and gender from your query text.
* **Filter Dropdowns**: Allows you to filter results by Brand, Type, Material, Gender, and Color.
* **Detailed Product View**: Click any shoe card to open its specifications and StockX link.
* **Similar Products Explore**: Shows visually and functionally similar shoes matching the current shoe's target gender.
* **Fully Plug-and-Play**: Ships with pre-cached embeddings and datasets. Starts instantly in Docker.

---

## Technology Stack
I chose these technologies for this project:
* **Frontend**: React, React Router v6, and Vanilla CSS.
* **Backend**: FastAPI (Python), Uvicorn.
* **Machine Learning**: Sentence-Transformers (`all-MiniLM-L6-v2`), rank-bm25 (`BM25Okapi`).
* **Data Processing**: Pandas (Parquet format), NumPy.
* **Containers**: Docker, Docker Compose.

---

## Recommendation Pipeline
I built a simplified and deterministic recommendation pipeline based on three search strategies. We replaced TF-IDF keyword overlap with BM25 lexical ranking: BM25 provides better keyword-based ranking by considering both keyword importance and document length, making it a stronger lexical retrieval method.
1. **Strategy 1: Structured Search**: Triggered when the semantic search query is empty. It applies hard filters (Brand, Type, Gender, Primary Color) and returns results directly without semantic vector similarity calculations or lexical searches.
2. **Strategy 2: Hybrid Search**: Triggered when structured filters are selected and a semantic search text remains. It applies hard filters first, then calculates semantic similarity (combining 70% Description embeddings and 30% BM25 ranking) only on the filtered subset.
3. **Strategy 3: Pure Semantic Search**: Triggered when no structured filters are detected. It performs hybrid BM25 and Description embedding search across the entire dataset using the same weights.
4. **Fallback Logic**: If fewer than 10 products are found, it takes the highest-ranked candidate, extracts its traits (Brand, Type, Gender, Material, Primary Color, Secondary Color), queries similar shoes, and fills the remaining slots up to 10 products.
5. **Similar Products (Top 20)**: Recommends visually and structurally similar shoes using Brand, Type, Gender, Material, Primary Color, Secondary Color, and both Identity and Description embeddings.

---

## Project Structure
Here is how the files are structured:
* `backend/data/` - Holds all the dataset CSV, Parquet, embeddings, and BM25 index.
* `backend/engine/` - Holds files for core recommendation algorithms and vector math.
* `backend/main.py` - Handles API routing.
* `frontend/src/components/` - Smaller reusable UI cards, search bars, and spinner.
* `frontend/src/pages/` - Full page components like the Product Details view.
* `frontend/src/services/` - Contains `api.js` for clean backend integration.
* `docs/` - Holds all the detailed guide files.

---

## Installation & How to Run

1. **Clone this repository**:
   ```bash
   git clone https://github.com/SATYAM-TYAGI/SneakX.git
   cd SneakX
   ```

2. **Boot up using Docker**:
   Make sure Docker Desktop is running, then run:
   ```bash
   docker compose up --build
   ```

3. **Open in browser**:
   Once running, open your browser and navigate to:
   `http://localhost:3000`

For more details, check out my [docs/INSTALLATION_GUIDE.md](file:///e:/SneakX/docs/INSTALLATION_GUIDE.md).

---

## Example Searches to Try
Type these into the search bar:
* `comfortable white running shoes`
* `retro nike high top sneakers`
* `black canvas skate shoes for casual wear`

---

## Screenshots

### HomePage
![HomePage](/screenshots/homepage.png)

### Product Details Page
![ProductDetails](/screenshots/productdetail.png)

---

## Source Declaration

### Dataset
The Original Dataset was obtained from kaggle. Link: [Original Dataset](https://www.kaggle.com/datasets/rajbhaumik123456/sneaker-dataset)

### Data Collection API
I populated the dataset using data collected from KicksDB API. Link: [KicksDB API](https://kicksdb.com/)