# Data Preparation

This document explains what is inside the sneaker dataset and how the embeddings are prepared.

## The Sneaker Dataset (`Sneaker_Dataset.csv`)
I used a dataset of over 4,000 sneakers. You can find this file in the `backend/data/` folder. Here are the columns inside the file:

* **Product ID**: The unique code for each shoe (like `P0001`).
* **Brand**: Who made the shoe (like `Nike` or `adidas`).
* **Model**: The name of the shoe family (like `Jordan 1 Mid`).
* **Display Name**: The full name of the shoe (like `Jordan 1 Mid Gym Red Black`).
* **Description**: A short paragraph about the shoe's design, history, and style.
* **Type**: The category (like `Basketball` or `Running`).
* **Gender**: Who it is for (like `men`, `women`, `unisex`, or `kids`).
* **Material**: What it is made of (like `Leather` or `Mesh`).
* **Retail Price**: The price of the shoe (like `170`).
* **Colorway**: The detailed color scheme (like `Black/White-Gym Red`).
* **Primary Color**: The main color used for filter matches (like `Black`).
* **Secondary Color**: The secondary color used in traits (like `Red`).
* **Thumbnail URL**: A link to a picture of the shoe.
* **StockX Link**: A link to see the shoe on StockX.

## Precomputed Files
During preprocessing (`python dev/prepare_data.py`), I generate the following files:

* **`processed_dataset.parquet`**: The cleaned dataset in Apache Parquet format.
* **`embeddings_identity.npy`**: The 384-dimensional vector representations of each shoe's identity fields (Brand, Model, Type, Gender, Material, Colors).
* **`embeddings_description.npy`**: The 384-dimensional vector representations of each shoe's description only.
* **`bm25_index.pkl`**: BM25 index built on Model, Description, Material, Primary Color, and Secondary Color for lexical matching. BM25 was chosen because it provides better keyword-based ranking by considering both keyword importance and document length, making it a stronger lexical retrieval method.
