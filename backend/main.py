import os
import sys
import re
import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Import internal recommendation engine and embedding modules
from engine import recommendation_engine
from engine import semantic_search as embedding

# Initialize the FastAPI application
app = FastAPI(title="SneakX API", description="AI-powered sneaker recommendation engine")

# Add CORS middleware so React frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store the data in memory
df_sneakers = None
embeddings_identity = None
embeddings_description = None
bm25_index = None

# Global dynamic lists for query parsing
UNIQUE_BRANDS = []
UNIQUE_COLORS = []

class FilterOptions(BaseModel):
    brand: Optional[str] = None
    type: Optional[str] = None
    gender: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None

class RecommendationRequest(BaseModel):
    query: Optional[str] = ""
    filters: Optional[FilterOptions] = None



def parse_query(query: str, unique_brands, unique_colors) -> tuple:
    """
    Simple query parser that extracts Brand, Type, Gender, and Primary Color.
    Removes those matching words and noise words, returning (parsed_filters, semantic_query).
    """
    if not query:
        return {}, ""

    cleaned = query.lower().strip()
    # Replace punctuation with spaces
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    words = cleaned.split()

    inferred = {}
    words_to_remove = set()

    # 1. Check Brand (longest first to avoid partial matching)
    for b in sorted(unique_brands, key=len, reverse=True):
        b_lower = b.lower()
        if b_lower in cleaned:
            # Word boundary check to avoid partial word match (e.g. "On" in "One")
            if re.search(r'\b' + re.escape(b_lower) + r'\b', cleaned):
                inferred["brand"] = b
                for w in b_lower.split():
                    words_to_remove.add(w)
                break

    # 2. Check Gender
    gender_syns = {
        "men": ["men", "man", "male"],
        "women": ["women", "woman", "female"],
        "kids": ["kids", "kid", "child", "children"],
        "unisex": ["unisex"]
    }
    for g_val, syns in gender_syns.items():
        for syn in syns:
            if syn in words:
                inferred["gender"] = g_val
                words_to_remove.add(syn)
                break
        if "gender" in inferred:
            break

    # 3. Check Type
    type_syns = {
        "running": ["running", "runner", "runners"],
        "basketball": ["basketball"],
        "skate": ["skate", "skating", "skater"],
        "lifestyle": ["lifestyle"],
        "slides": ["slides", "slide"],
        "training": ["training", "trainer", "trainers"],
        "soccer": ["soccer"],
        "casual": ["casual"],
        "trail": ["trail"],
        "walking": ["walking"]
    }
    for t_val, syns in type_syns.items():
        for syn in syns:
            if syn in words:
                inferred["type"] = t_val
                words_to_remove.add(syn)
                # Helper words for type
                words_to_remove.add("shoes")
                words_to_remove.add("shoe")
                break
        if "type" in inferred:
            break

    # 4. Check Primary Color
    for c in unique_colors:
        c_lower = c.lower()
        if c_lower in words:
            inferred["primary_color"] = c
            words_to_remove.add(c_lower)
            break

    # If any structured filter was found, we also remove noise/helper words
    if inferred:
        noise_words = {"for", "in", "color", "shoes", "shoe"}
        for nw in noise_words:
            if nw in words:
                words_to_remove.add(nw)

    # Reconstruct remaining semantic query
    semantic_words = [w for w in query.split() if w.lower().strip(",.?!()-\"'/") not in words_to_remove]
    semantic_query = " ".join(semantic_words).strip()

    return inferred, semantic_query

@app.on_event("startup")
def startup_event():
    """
    Load dataset, double embeddings, and BM25 index into memory when FastAPI starts.
    """
    global df_sneakers, embeddings_identity, embeddings_description, bm25_index, UNIQUE_BRANDS, UNIQUE_COLORS

    data_dir = "data"
    parquet_path = os.path.join(data_dir, "processed_dataset.parquet")
    emb_id_path = os.path.join(data_dir, "embeddings_identity.npy")
    emb_desc_path = os.path.join(data_dir, "embeddings_description.npy")
    bm25_path = os.path.join(data_dir, "bm25_index.pkl")

    # Validation checks
    missing_files = []
    for p in [parquet_path, emb_id_path, emb_desc_path, bm25_path]:
        if not os.path.exists(p):
            missing_files.append(p)

    if missing_files:
        error_msg = (
            "\n"
            "===================================================================\n"
            f"ERROR: Missing backend data files: {', '.join(missing_files)}.\n"
            "Please ensure the pre-cached dataset files are inside backend/data/.\n"
            "===================================================================\n"
        )
        print(error_msg)
        sys.exit(1)

    # Load DataFrame
    df_sneakers = pd.read_parquet(parquet_path)
    print(f"Successfully loaded {len(df_sneakers)} sneakers from Parquet.")

    # Load two numpy embedding matrices
    embeddings_identity = np.load(emb_id_path)
    embeddings_description = np.load(emb_desc_path)
    print("Successfully loaded identity and description sneaker embeddings.")

    # Load BM25 index
    with open(bm25_path, "rb") as f:
        bm25_index = pickle.load(f)
    print("Successfully loaded BM25 index.")

    # Populate unique lists for query parser
    UNIQUE_BRANDS = sorted(df_sneakers["Brand"].dropna().unique().tolist())
    UNIQUE_COLORS = sorted(df_sneakers["Primary Color"].dropna().unique().tolist())

    # Warm up Sentence Transformer
    embedding.get_sentence_transformer_model()
    print("Sentence Transformer model loaded successfully and ready.")

def format_sneaker_payload(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert sneaker rows in DataFrame to simple dict payloads for the frontend.
    """
    payload = []
    for _, row in df.iterrows():
        payload.append({
            "product_id": str(row["Product ID"]),
            "brand": str(row["Brand"]),
            "model": str(row["Model"]),
            "display_name": str(row["Display Name"]),
            "description": str(row["Description"]),
            "type": str(row["Type"]),
            "gender": str(row["Gender"]),
            "material": str(row["Material"]),
            "color": str(row["Colorway"]) if pd.notnull(row["Colorway"]) else "Unknown",
            "retail_price": f"${str(row['Retail Price']).strip()}" if not str(row['Retail Price']).strip().startswith("$") else str(row['Retail Price']).strip(),
            "thumbnail_url": str(row["Thumbnail URL"]),
            "image1_url": "",
            "image2_url": "",
            "image3_url": "",
            "stockx_url": str(row["StockX Link"]) if pd.notnull(row["StockX Link"]) else ""
        })
    return payload

@app.get("/")
def read_root():
    """
    A simple health check endpoint.
    """
    return {"message": "Welcome to the SneakX Recommendation API!"}

@app.post("/api/recommend")
def get_recommendations(request: RecommendationRequest):
    """
    Process search filters, extract query properties, apply hard filters and run semantic strategy.
    Returns the Top 10 recommendations and Top 20 similar products.
    """
    if df_sneakers is None or embeddings_identity is None or embeddings_description is None:
        raise HTTPException(status_code=500, detail="Recommendation engine artifacts not loaded.")

    search_query = request.query.strip() if request.query else ""
    user_filters = {}
    if request.filters:
        user_filters = {
            "brand": request.filters.brand,
            "type": request.filters.type,
            "gender": request.filters.gender,
            "color": request.filters.color,
            "material": request.filters.material
        }

    # Extract structured filters from user query
    inferred_filters, semantic_query = parse_query(search_query, UNIQUE_BRANDS, UNIQUE_COLORS)

    # Merge inferred filters with user selected filters (dropdown selections prioritize)
    merged_brand = user_filters.get("brand") or inferred_filters.get("brand")
    merged_type = user_filters.get("type") or inferred_filters.get("type")
    merged_gender = user_filters.get("gender") or inferred_filters.get("gender")
    merged_color = user_filters.get("color") or inferred_filters.get("primary_color")
    merged_material = user_filters.get("material")

    has_structured_filters = any([merged_brand, merged_type, merged_gender, merged_color, merged_material])

    # STAGE 1: Always apply structured filters first as hard filters
    filtered_df, filtered_indices = recommendation_engine.filter_dataset(
        df_sneakers,
        brand=merged_brand,
        shoe_type=merged_type,
        gender=merged_gender,
        primary_color=merged_color,
        material=merged_material
    )

    if not semantic_query:
        # STRATEGY 1: Structured Search
        final_recommendations = filtered_df.head(10).copy()
    else:
        # Compute query vector
        query_vector = embedding.compute_embedding(semantic_query)

        if has_structured_filters:
            # STRATEGY 2: Hybrid Search
            final_recommendations = recommendation_engine.search_semantic(
                query_embedding=query_vector,
                semantic_query=semantic_query,
                embeddings_description=embeddings_description,
                bm25_index=bm25_index,
                df=df_sneakers,
                filtered_indices=filtered_indices
            ).head(10)
        else:
            # STRATEGY 3: Pure Semantic Search
            all_indices = list(range(len(df_sneakers)))
            final_recommendations = recommendation_engine.search_semantic(
                query_embedding=query_vector,
                semantic_query=semantic_query,
                embeddings_description=embeddings_description,
                bm25_index=bm25_index,
                df=df_sneakers,
                filtered_indices=all_indices
            ).head(10)

    # FALLBACK LOGIC: If fewer than 10 products are found
    if len(final_recommendations) < 10 and len(final_recommendations) > 0:
        highest_ranked = final_recommendations.iloc[0]
        highest_ranked_id = highest_ranked["Product ID"]
        
        exclude_ids = final_recommendations["Product ID"].tolist()
        similar_fill_df = recommendation_engine.find_similar_products(
            target_product_id=highest_ranked_id,
            df=df_sneakers,
            embeddings_identity=embeddings_identity,
            embeddings_description=embeddings_description,
            exclude_ids=exclude_ids,
            top_k=10 - len(final_recommendations)
        )
        if len(similar_fill_df) > 0:
            final_recommendations = pd.concat([final_recommendations, similar_fill_df], ignore_index=True)

    # Global fallback if still fewer than 10 products
    if len(final_recommendations) < 10:
        exclude_ids = final_recommendations["Product ID"].tolist() if len(final_recommendations) > 0 else []
        global_fill_df = df_sneakers[~df_sneakers["Product ID"].isin(exclude_ids)].head(10 - len(final_recommendations))
        if len(global_fill_df) > 0:
            final_recommendations = pd.concat([final_recommendations, global_fill_df], ignore_index=True)

    # STAGE 4: Discover Similar Products (Top 20 similar products for the selected item)
    similar_df = pd.DataFrame()
    if len(final_recommendations) > 0:
        target_id = final_recommendations.iloc[0]["Product ID"]
        exclude_ids = final_recommendations["Product ID"].tolist()
        
        similar_df = recommendation_engine.find_similar_products(
            target_product_id=target_id,
            df=df_sneakers,
            embeddings_identity=embeddings_identity,
            embeddings_description=embeddings_description,
            exclude_ids=exclude_ids,
            top_k=20
        )

    recommendations_payload = format_sneaker_payload(final_recommendations)
    similar_products_payload = format_sneaker_payload(similar_df)

    return {
        "recommendations": recommendations_payload,
        "similar_products": similar_products_payload
    }

@app.get("/api/filters")
def get_filter_options():
    """
    Get unique options from the dataset to build frontend filters dynamically.
    """
    global df_sneakers

    if df_sneakers is None:
        raise HTTPException(status_code=500, detail="Sneaker dataset is not loaded.")

    brands = sorted(df_sneakers["Brand"].dropna().unique().tolist())
    types = sorted(df_sneakers["Type"].dropna().unique().tolist())
    materials = sorted(df_sneakers["Material"].dropna().unique().tolist())
    # Primary Color should be treated as the color filter. Do not use Colorway for filtering.
    colors = sorted(df_sneakers["Primary Color"].dropna().unique().tolist())

    return {
        "brands": brands,
        "types": types,
        "materials": materials,
        "colors": colors
    }

@app.get("/api/similar/{product_id}")
def get_similar_products(product_id: str):
    """
    Get similar products for a specific sneaker by its product ID.
    Returns 20 similar products.
    """
    global df_sneakers, embeddings_identity, embeddings_description
    
    if df_sneakers is None or embeddings_identity is None or embeddings_description is None:
        raise HTTPException(status_code=500, detail="Recommendation engine artifacts not loaded.")

    similar_df = recommendation_engine.find_similar_products(
        target_product_id=product_id,
        df=df_sneakers,
        embeddings_identity=embeddings_identity,
        embeddings_description=embeddings_description,
        exclude_ids=[product_id],
        top_k=20
    )
    
    return {
        "similar_products": format_sneaker_payload(similar_df)
    }
