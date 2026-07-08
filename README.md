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
* **Machine Learning**: Sentence-Transformers (`all-MiniLM-L6-v2`), Scikit-Learn (`TfidfVectorizer`).
* **Data Processing**: Pandas (Parquet format), NumPy.
* **Containers**: Docker, Docker Compose.

---

## Recommendation Pipeline
I built a 5-stage pipeline to select and rank recommendations:
1. **Filtering**: Applies hard filters (selected Brand and Type). If results are empty, it automatically falls back to search the whole database.
2. **Similarity Math**: it Computes semantic embedding cosine similarity and TF-IDF keyword overlap.
3. **Re-ranking**: Adds bonus points for matching attributes.
4. **Diversity Check**: Skips duplicate model families and applies a brand count penalty.
5. **Similar Products**: Finds similar shoes matching the target shoe's gender.

---

## Project Structure
Here is how the files are structured:
* `backend/data/` - Holds all the dataset CSV, Parquet, embeddings, and TF-IDF data.
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
   git clone https://github.com/SATYAM-TYAGI/SneaksHub.git
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