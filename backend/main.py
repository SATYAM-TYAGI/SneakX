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

# import internal recommendation engine and embedding modules
from engine import recommendation_engine
from engine import semantic_search as embedding

# initialize the fastapi application
app = FastAPI(title="SneakX API", description="AI-powered sneaker recommendation engine")

# add CORS middleware so React frontend can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global variables to store the data in memory
df_sneakers = None
embeddings_identity = None
embeddings_description = None
embeddings_combined = None
tfidf_vectorizer = None
tfidf_matrix = None

class FilterOptions(BaseModel):
    brand: Optional[str] = None
    type: Optional[str] = None
    gender: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None

class RecommendationRequest(BaseModel):
    query: Optional[str] = ""
    filters: Optional[FilterOptions] = None

def clean_text_for_tfidf(text: str) -> str:
    """
    Clean query text prior to TF-IDF transformations.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # remove html tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_filters_from_query(query: str, filter_options: dict) -> dict:
    """
    Smart Query Understanding: Parse filters brand, type, material, color, and gender directly from search query.
    Colors are matched exactly using individual tokens to prevent incorrect matches.
    """
    inferred = {}
    if not query:
        return inferred
        
    cleaned = re.sub(r'[^\w\s]', ' ', query.lower())
    words = cleaned.split()
    
    brands = [b.lower() for b in filter_options.get("brands", [])]
    types = [t.lower() for t in filter_options.get("types", [])]
    materials = [m.lower() for m in filter_options.get("materials", [])]
    
    # map colors list tokens
    db_colors = filter_options.get("colors", [])
    colors = set()
    for col in db_colors:
        if pd.notnull(col):
            for part in re.split(r'[/ -]', str(col).lower()):
                if part.strip():
                    colors.add(part.strip())
                    
    # explicit check for multi-word brand: New Balance
    if "new balance" in cleaned:
        inferred["brand"] = "New Balance"
        
    for word in words:
        if word in brands and "brand" not in inferred:
            idx = brands.index(word)
            inferred["brand"] = filter_options["brands"][idx]
            
        if word in types and "type" not in inferred:
            idx = types.index(word)
            inferred["type"] = filter_options["types"][idx]
            
        if word in materials and "material" not in inferred:
            idx = materials.index(word)
            inferred["material"] = filter_options["materials"][idx]
            
        if word in colors and "color" not in inferred:
            # verify exact token match in DB colors
            for col in db_colors:
                if pd.notnull(col):
                    tokens = [t.strip().lower() for t in re.split(r'[/ -]', str(col))]
                    if word in tokens:
                        inferred["color"] = col
                        break
                        
        # check genders
        if word in ["men", "man", "male"]:
            inferred["gender"] = "men"
        elif word in ["women", "woman", "female"]:
            inferred["gender"] = "women"
        elif word in ["unisex"]:
            inferred["gender"] = "unisex"
        elif word in ["kids", "kid", "child"]:
            inferred["gender"] = "kids"
            
    return inferred

@app.on_event("startup")
def startup_event():
    """
    Load dataset, multiple embeddings, and TF-IDF matrix into memory when FastAPI starts.
    If any file is missing, crash the startup immediately.
    """
    global df_sneakers, embeddings_identity, embeddings_description, embeddings_combined, tfidf_vectorizer, tfidf_matrix

    data_dir = "data"
    parquet_path = os.path.join(data_dir, "processed_dataset.parquet")
    emb_id_path = os.path.join(data_dir, "embeddings_identity.npy")
    emb_desc_path = os.path.join(data_dir, "embeddings_description.npy")
    emb_comb_path = os.path.join(data_dir, "embeddings_combined.npy")
    tfidf_vec_path = os.path.join(data_dir, "tfidf_vectorizer.pkl")
    tfidf_mat_path = os.path.join(data_dir, "tfidf_matrix.pkl")

    # validation checks
    missing_files = []
    for p in [parquet_path, emb_id_path, emb_desc_path, emb_comb_path, tfidf_vec_path, tfidf_mat_path]:
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

    # load DataFrame
    df_sneakers = pd.read_parquet(parquet_path)
    print(f"Successfully loaded {len(df_sneakers)} sneakers from Parquet.")

    # load three numpy embedding matrices
    embeddings_identity = np.load(emb_id_path)
    embeddings_description = np.load(emb_desc_path)
    embeddings_combined = np.load(emb_comb_path)
    print("Successfully loaded three-way sneaker embeddings.")

    # load TF-IDF assets
    with open(tfidf_vec_path, "rb") as f:
        tfidf_vectorizer = pickle.load(f)
    with open(tfidf_mat_path, "rb") as f:
        tfidf_matrix = pickle.load(f)
    print("Successfully loaded TF-IDF vectorizer and document matrices.")

    # warm up Sentence Transformer
    embedding.get_sentence_transformer_model()
    print("Sentence Transformer model loaded successfully and ready.")

def format_sneaker_payload(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert sneaker rows in DataFrame to simple dict payloads.
    Exclude raw embeddings, similarity scores, or intermediate ranking metrics.
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
            "color": str(row["Color"]) if pd.notnull(row["Color"]) else "Unknown",
            "retail_price": str(row["Retail Price"]).strip(),
            "thumbnail_url": str(row["Thumbnail URL"]),
            "image1_url": str(row["Image 1 URL"]) if pd.notnull(row["Image 1 URL"]) else "",
            "image2_url": str(row["Image 2 URL"]) if pd.notnull(row["Image 2 URL"]) else "",
            "image3_url": str(row["Image 3 URL"]) if pd.notnull(row["Image 3 URL"]) else "",
            "stockx_url": str(row["StockX Link"])
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
    Process search filters, semantic query, and metadata re-ranking.
    Returns the Top 5 recommendations and Top 20 similar products in a single response.
    """
    if df_sneakers is None or embeddings_identity is None or tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="Recommendation engine artifacts not loaded.")

    # extract query and filters from request
    search_query = request.query.strip() if request.query else ""
    user_filters = {}
    if request.filters:
        user_filters = {
            "brand": request.filters.brand,
            "type": request.filters.type,
            "gender": request.filters.gender,
            "material": request.filters.material,
            "color": request.filters.color
        }

    # Smart Query Understanding
    filter_metadata = {
        "brands": sorted(df_sneakers["Brand"].dropna().unique().tolist()),
        "types": sorted(df_sneakers["Type"].dropna().unique().tolist()),
        "materials": sorted(df_sneakers["Material"].dropna().unique().tolist()),
        "colors": sorted(df_sneakers["Color"].dropna().unique().tolist())
    }
    inferred_filters = parse_filters_from_query(search_query, filter_metadata)

    # merge inferred filters with user selected filters (dropdown selections prioritize)
    merged_brand = user_filters.get("brand") or inferred_filters.get("brand")
    merged_type = user_filters.get("type") or inferred_filters.get("type")
    
    hard_gender = user_filters.get("gender")
    hard_material = user_filters.get("material")
    hard_color = user_filters.get("color")

    # preferences filters for Stage 3 re-ranking
    filters_for_search = {
        "brand": merged_brand,
        "type": merged_type,
        "gender": user_filters.get("gender") or inferred_filters.get("gender"),
        "material": user_filters.get("material") or inferred_filters.get("material"),
        "color": user_filters.get("color") or inferred_filters.get("color")
    }

    # STAGE 1: Optional Filtering (Hard filters only)
    filtered_df, filtered_indices = recommendation_engine.filter_dataset(
        df_sneakers,
        brand=merged_brand,
        shoe_type=merged_type,
        gender=hard_gender,
        material=hard_material,
        color=hard_color
    )

    # STAGE 2: Semantic Similarity Search
    if search_query:
        query_text = search_query
    else:
        query_text = embedding.build_search_sentence(
            brand=merged_brand,
            shoe_type=merged_type,
            gender=filters_for_search.get("gender"),
            material=filters_for_search.get("material"),
            color=filters_for_search.get("color")
        )

    # generate clean TF-IDF query text and embed query vector
    cleaned_query = clean_text_for_tfidf(query_text)
    query_vector = embedding.compute_embedding(query_text)
    query_tfidf = tfidf_vectorizer.transform([cleaned_query])

    # extract Top 100 candidate matches from the filtered subset
    top_100_df, top_100_semantic_scores, top_100_tfidf_scores = recommendation_engine.search_semantic(
        query_embedding=query_vector,
        query_tfidf=query_tfidf,
        embeddings_identity=embeddings_identity,
        embeddings_description=embeddings_description,
        embeddings_combined=embeddings_combined,
        tfidf_matrix=tfidf_matrix,
        df=filtered_df,
        filtered_indices=filtered_indices,
        top_k=100
    )

    # STAGE 3: Re-ranking
    top_ranked_df = recommendation_engine.rerank_candidates(
        top_100_df,
        top_100_semantic_scores,
        top_100_tfidf_scores,
        filters_for_search,
        top_k=100
    )

    # apply diversity filter to select up to 5 recommendations
    final_recommendations = recommendation_engine.apply_diversity_filter(top_ranked_df, top_k=5)

    # fill remaining slots from global recommendations if the list is incomplete (< 5)
    if len(final_recommendations) < 5:
        global_indices = list(range(len(df_sneakers)))
        global_100_df, global_100_semantic, global_100_tfidf = recommendation_engine.search_semantic(
            query_embedding=query_vector,
            query_tfidf=query_tfidf,
            embeddings_identity=embeddings_identity,
            embeddings_description=embeddings_description,
            embeddings_combined=embeddings_combined,
            tfidf_matrix=tfidf_matrix,
            df=df_sneakers,
            filtered_indices=global_indices,
            top_k=100
        )
        global_ranked_df = recommendation_engine.rerank_candidates(
            global_100_df,
            global_100_semantic,
            global_100_tfidf,
            {}, # empty filters for global match
            top_k=100
        )
        diverse_global = recommendation_engine.apply_diversity_filter(global_ranked_df, top_k=100)
        
        # append global recommendations without returning duplicates
        existing_ids = set(final_recommendations["Product ID"].tolist())
        existing_base_models = set([recommendation_engine.normalize_base_model(m) for m in final_recommendations["Model"].tolist()])
        
        fill_rows = []
        for _, row in diverse_global.iterrows():
            prod_id = row["Product ID"]
            base_model = recommendation_engine.normalize_base_model(row["Model"])
            if prod_id not in existing_ids and base_model not in existing_base_models:
                fill_rows.append(row)
                existing_ids.add(prod_id)
                existing_base_models.add(base_model)
                if len(final_recommendations) + len(fill_rows) >= 5:
                    break
                    
        if fill_rows:
            fill_df = pd.DataFrame(fill_rows)
            final_recommendations = pd.concat([final_recommendations, fill_df], ignore_index=True)

    # STAGE 4: Discover Similar Products
    similar_df = pd.DataFrame()
    if len(final_recommendations) > 0:
        number_one_id = final_recommendations.iloc[0]["Product ID"]
        exclude_ids = final_recommendations["Product ID"].tolist()
        
        # restrict similar products target list to match gender of active sneaker
        number_one_gender = final_recommendations.iloc[0]["Gender"]
        
        similar_df = recommendation_engine.find_similar_products(
            target_product_id=number_one_id,
            df=df_sneakers,
            embeddings_identity=embeddings_identity,
            embeddings_description=embeddings_description,
            embeddings_combined=embeddings_combined,
            exclude_ids=exclude_ids,
            target_gender=number_one_gender,
            top_k=20
        )

    # format data payload objects
    recommendations_payload = format_sneaker_payload(final_recommendations)
    similar_products_payload = format_sneaker_payload(similar_df)

    # return both lists in a single JSON response
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

    # fetch unique values from dataframe columns
    brands = sorted(df_sneakers["Brand"].dropna().unique().tolist())
    types = sorted(df_sneakers["Type"].dropna().unique().tolist())
    materials = sorted(df_sneakers["Material"].dropna().unique().tolist())
    colors = sorted(df_sneakers["Color"].dropna().unique().tolist())

    return {
        "brands": brands,
        "types": types,
        "materials": materials,
        "colors": colors
    }
