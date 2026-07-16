# SneakX API Documentation

I built a simple API for SneakX using FastAPI. Here is how the frontend talks to the backend.

## Base URL
When you run the app using Docker, the backend runs here:
`http://localhost:8000`

---

## Endpoints

### 1. Get Recommendations and Similar Shoes
I made this endpoint to handle the search. You can send a search query, dropdown filter selections, or both. It returns the top 10 recommended shoes and 20 similar shoes in one response.

* **URL:** `/api/recommend`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Request Body Example:**
  ```json
  {
    "query": "comfortable white running shoes",
    "filters": {
      "brand": "Nike",
      "type": "Running",
      "gender": "men",
      "material": "Mesh",
      "color": "White"
    }
  }
  ```

* **Response Body Example:**
  ```json
  {
    "recommendations": [
      {
        "product_id": "P0002",
        "brand": "adidas",
        "model": "adidas Ultra Boost 21",
        "display_name": "adidas Ultra Boost 21 Triple White",
        "description": "A very comfortable running shoe...",
        "type": "Running",
        "gender": "men",
        "material": "Primeknit",
        "color": "Triple White",
        "retail_price": "180",
        "thumbnail_url": "https://...",
        "image1_url": "",
        "image2_url": "",
        "image3_url": "",
        "stockx_url": "https://..."
      }
    ],
    "similar_products": [
      {
        "product_id": "P0015",
        "brand": "Nike",
        "model": "Nike Pegasus 38",
        "display_name": "Nike Pegasus 38 Flyease Black White",
        "description": "Good for daily running...",
        "type": "Running",
        "gender": "men",
        "material": "Mesh",
        "color": "Black/White",
        "retail_price": "120",
        "thumbnail_url": "https://...",
        "image1_url": "",
        "image2_url": "",
        "image3_url": "",
        "stockx_url": "https://..."
      }
    ]
  }
  ```

---

### 2. Get Filter Options
I created this endpoint so the frontend dropdowns do not have to be hardcoded. It returns all the unique brands, types, materials, and colors from the database.

* **URL:** `/api/filters`
* **Method:** `GET`
* **Response Body Example:**
  ```json
  {
    "brands": ["Jordan", "adidas", "Nike", "Vans"],
    "types": ["Basketball", "Running", "Casual"],
    "materials": ["Leather", "Mesh", "Suede"],
    "colors": ["Black", "White", "Red"]
  }
  ```

---

### 3. Get Similar Products
I created this endpoint so the details page can dynamically load visually and functionally similar shoes for the sneaker currently being viewed.

* **URL:** `/api/similar/{product_id}`
* **Method:** `GET`
* **Response Body Example:**
  ```json
  {
    "similar_products": [
      {
        "product_id": "P0015",
        "brand": "Nike",
        "model": "Nike Pegasus 38",
        "display_name": "Nike Pegasus 38 Flyease Black White",
        "description": "Good for daily running...",
        "type": "Running",
        "gender": "men",
        "material": "Mesh",
        "color": "Black/White",
        "retail_price": "$120",
        "thumbnail_url": "https://...",
        "image1_url": "",
        "image2_url": "",
        "image3_url": "",
        "stockx_url": "https://..."
      }
    ]
  }
  ```
