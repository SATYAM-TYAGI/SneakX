import re
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Re-ranking Bonus Values (Named Constants)
BONUS_TYPE_MATCH = 0.12
BONUS_BRAND_MATCH = 0.10
BONUS_COLOR_MATCH = 0.08
BONUS_MATERIAL_MATCH = 0.05
BONUS_GENDER_MATCH = 0.03
BONUS_KEYWORD_OVERLAP = 0.02

# Semantic Embeddings Combination Weights
WEIGHT_COMBINED = 0.40
WEIGHT_DESCRIPTION = 0.30
WEIGHT_IDENTITY = 0.30

def normalize_base_model(model_name: str) -> str:
    """
    Helper function to normalize sneaker model names.
    Removes unnecessary qualifiers like Low, High, Mid, SE, GS, Premium, Retro, '07,
    common colors, and special edition details to isolate the base sneaker family.
    """
    if not isinstance(model_name, str):
        return ""
    
    # lowercase and strip spaces
    normalized = model_name.lower().strip()
    
    # words to strip completely from base model evaluation
    words_to_remove = {
        "low", "high", "mid", "se", "gs", "premium", "retro", "'07", "07",
        "white", "black", "grey", "gray", "red", "blue", "green", "yellow", 
        "pink", "purple", "orange", "cream", "navy", "silver", "gold",
        "og", "special", "edition", "v2", "v1", "w", "gs", "ps", "td"
    }
    
    # split and filter out tokens
    tokens = normalized.split()
    clean_tokens = []
    for t in tokens:
        # remove punctuation from word token
        t_clean = re.sub(r'[^\w\s]', '', t).strip()
        if t_clean and t_clean not in words_to_remove:
            clean_tokens.append(t_clean)
            
    return " ".join(clean_tokens).strip()

def apply_diversity_filter(df: pd.DataFrame, top_k: int) -> pd.DataFrame:
    """
    Filters a DataFrame of recommendations to only allow one sneaker from each base model,
    and applies brand diversity selection when scores are very close.
    """
    if len(df) == 0:
        return df

    selected_rows = []
    selected_base_models = set()
    selected_brands = {}
    
    candidates = df.copy()
    
    # Determine the score column to use
    score_col = "rank_score" if "rank_score" in candidates.columns else "similarity_score"
    if score_col not in candidates.columns:
        score_col = candidates.columns[0]
        
    # Brand penalty constant: 0.03
    BRAND_PENALTY = 0.03
    
    while len(selected_rows) < top_k and len(candidates) > 0:
        best_idx = None
        best_adjusted_score = -999.0
        
        for idx, row in candidates.iterrows():
            base_model = normalize_base_model(row["Model"])
            # Skip if base model already selected
            if base_model in selected_base_models:
                continue
                
            brand = row["Brand"]
            brand_count = selected_brands.get(brand, 0)
            
            # Apply brand count penalty
            original_score = row[score_col]
            adjusted_score = original_score - (brand_count * BRAND_PENALTY)
            
            if adjusted_score > best_adjusted_score:
                best_adjusted_score = adjusted_score
                best_idx = idx
                
        if best_idx is None:
            break
            
        # Select the best candidate
        selected_row = candidates.loc[best_idx]
        selected_rows.append(selected_row)
        
        # Update selections
        selected_base_models.add(normalize_base_model(selected_row["Model"]))
        brand = selected_row["Brand"]
        selected_brands[brand] = selected_brands.get(brand, 0) + 1
        
        # Remove from candidates
        candidates = candidates.drop(best_idx)
        
    return pd.DataFrame(selected_rows).reset_index(drop=True)

def filter_dataset(df: pd.DataFrame, brand: str = None, shoe_type: str = None, gender: str = None, material: str = None, color: str = None):
    """
    Stage 1: Filter the dataset based on non-empty user options.
    If all filters combined remove every shoe, return the original full dataset.
    """
    filtered_df = df.copy()

    # apply brand filter (case-insensitive)
    if brand:
        filtered_df = filtered_df[filtered_df["Brand"].str.lower() == brand.lower()]

    # apply shoe type filter (case-insensitive)
    if shoe_type:
        filtered_df = filtered_df[filtered_df["Type"].str.lower() == shoe_type.lower()]

    # apply gender filter (case-insensitive)
    if gender:
        filtered_df = filtered_df[filtered_df["Gender"].str.lower() == gender.lower()]

    # apply material filter (case-insensitive)
    if material:
        filtered_df = filtered_df[filtered_df["Material"].str.lower() == material.lower()]

    # apply color filter (case-insensitive substring check)
    if color:
        filtered_df = filtered_df[filtered_df["Color"].str.lower().str.contains(color.lower(), na=False)]

    # if the filters removed all products, fall back to the full dataset
    if len(filtered_df) == 0:
        print("Warning: Filters returned 0 results. Falling back to the full dataset.")
        return df, df.index.tolist()

    return filtered_df, filtered_df.index.tolist()

def calculate_cosine_similarity(query_embedding: np.ndarray, embeddings_subset: np.ndarray) -> np.ndarray:
    """
    Calculate cosine similarity scores using sklearn's pairwise.cosine_similarity.
    """
    sims = cosine_similarity(query_embedding.reshape(1, -1), embeddings_subset)
    return sims[0]

def search_semantic(
    query_embedding: np.ndarray, 
    query_tfidf: np.ndarray,
    embeddings_identity: np.ndarray,
    embeddings_description: np.ndarray,
    embeddings_combined: np.ndarray,
    tfidf_matrix: np.ndarray,
    df: pd.DataFrame, 
    filtered_indices: list, 
    top_k: int = 100
):
    """
    Stage 2: Slice the pre-computed embeddings and TF-IDF matrix for the filtered items,
    calculate similarity scores, combine them, and extract the Top candidate pool (default top_k=100).
    """
    emb_id_subset = embeddings_identity[filtered_indices]
    emb_desc_subset = embeddings_description[filtered_indices]
    emb_comb_subset = embeddings_combined[filtered_indices]
    tfidf_subset = tfidf_matrix[filtered_indices]

    # calculate cosine similarity for the three embedding sets
    sim_id = calculate_cosine_similarity(query_embedding, emb_id_subset)
    sim_desc = calculate_cosine_similarity(query_embedding, emb_desc_subset)
    sim_comb = calculate_cosine_similarity(query_embedding, emb_comb_subset)

    # combine three similarity scores into one semantic score
    semantic_scores = (
        WEIGHT_COMBINED * sim_comb +
        WEIGHT_DESCRIPTION * sim_desc +
        WEIGHT_IDENTITY * sim_id
    )

    # calculate TF-IDF similarity
    tfidf_sims = cosine_similarity(query_tfidf, tfidf_subset)[0]

    # combine semantic and tf-idf similarity (using new bonus constants weights relative proportions)
    combined_sims = semantic_scores + BONUS_KEYWORD_OVERLAP * tfidf_sims

    # sort scores in descending order
    sorted_order = np.argsort(combined_sims)[::-1]
    top_candidates_idx = sorted_order[:top_k]

    df_subset = df.copy()
    top_df = df_subset.iloc[top_candidates_idx].copy()
    
    top_semantic_scores = semantic_scores[top_candidates_idx]
    top_tfidf_scores = tfidf_sims[top_candidates_idx]

    return top_df, top_semantic_scores, top_tfidf_scores

def rerank_candidates(candidates_df: pd.DataFrame, semantic_scores: np.ndarray, tfidf_scores: np.ndarray, filters: dict, top_k: int = 5):
    """
    Stage 3: Perform lightweight re-ranking on candidates using updated bonus constant weights.
    """
    ranked_df = candidates_df.copy()
    ranked_df["semantic_score"] = semantic_scores
    ranked_df["tfidf_score"] = tfidf_scores

    target_brand = filters.get("brand")
    target_type = filters.get("type")
    target_color = filters.get("color")
    target_gender = filters.get("gender")
    target_material = filters.get("material")

    re_rank_scores = []
    for idx, row in ranked_df.iterrows():
        # check brand match
        brand_match = 1.0 if not target_brand or (str(row["Brand"]).lower() == target_brand.lower()) else 0.0
        
        # check shoe type match
        type_match = 1.0 if not target_type or (str(row["Type"]).lower() == target_type.lower()) else 0.0

        # check color match (case-insensitive substring check)
        color_match = 1.0 if not target_color or (target_color.lower() in str(row["Color"]).lower()) else 0.0
        
        # check gender match
        gender_match = 1.0 if not target_gender or (str(row["Gender"]).lower() == target_gender.lower()) else 0.0

        # check material match
        material_match = 1.0 if not target_material or (str(row["Material"]).lower() == target_material.lower()) else 0.0

        # retrieve similarity scores
        semantic = row["semantic_score"]
        tfidf = row["tfidf_score"]

        # calculate final score using new bonus constants
        final_score = (
            semantic +
            BONUS_TYPE_MATCH * type_match +
            BONUS_BRAND_MATCH * brand_match +
            BONUS_COLOR_MATCH * color_match +
            BONUS_MATERIAL_MATCH * material_match +
            BONUS_GENDER_MATCH * gender_match +
            BONUS_KEYWORD_OVERLAP * tfidf
        )
        re_rank_scores.append(final_score)

    ranked_df["rank_score"] = re_rank_scores
    ranked_df = ranked_df.sort_values(by="rank_score", ascending=False)

    return ranked_df.head(top_k)

def find_similar_products(
    target_product_id: str, 
    df: pd.DataFrame, 
    embeddings_identity: np.ndarray,
    embeddings_description: np.ndarray,
    embeddings_combined: np.ndarray,
    exclude_ids: list, 
    target_gender: str = None,
    top_k: int = 20,
    diagnostic_mode: bool = False
):
    """
    Explore Similar Sneakers: Compare a target product against the dataset.
    Filters out current sneaker, shoes from same base model family, restricts by gender (if provided), 
    and applies diversity filtering to return 20 visually and functionally diverse recommendations.
    """
    # restrict candidates to target gender if specified
    if target_gender:
        df_candidates = df[df["Gender"].str.lower() == target_gender.lower()].copy()
    else:
        df_candidates = df.copy()

    # extract original indices of candidate rows
    candidate_indices = df_candidates.index.tolist()

    # locate index of target product
    matching_indices = np.where(df["Product ID"] == target_product_id)[0]
    if len(matching_indices) == 0:
        return pd.DataFrame(columns=df.columns)

    target_position = matching_indices[0]

    # retrieve target vectors
    target_emb_id = embeddings_identity[target_position]
    target_emb_desc = embeddings_description[target_position]
    target_emb_comb = embeddings_combined[target_position]

    # slice embeddings subset matching gender candidates
    emb_id_subset = embeddings_identity[candidate_indices]
    emb_desc_subset = embeddings_description[candidate_indices]
    emb_comb_subset = embeddings_combined[candidate_indices]

    # calculate cosine similarity
    sim_id = calculate_cosine_similarity(target_emb_id, emb_id_subset)
    sim_desc = calculate_cosine_similarity(target_emb_desc, emb_desc_subset)
    sim_comb = calculate_cosine_similarity(target_emb_comb, emb_comb_subset)

    # combine scores using semantic weights
    similarities = (
        WEIGHT_COMBINED * sim_comb +
        WEIGHT_DESCRIPTION * sim_desc +
        WEIGHT_IDENTITY * sim_id
    )

    # assign similarities to candidate DataFrame
    df_candidates = df_candidates.copy()
    df_candidates["similarity_score"] = similarities

    # sort candidates descending by similarity
    df_candidates = df_candidates.sort_values(by="similarity_score", ascending=False)

    # Exclude the current sneaker
    df_candidates = df_candidates[df_candidates["Product ID"] != target_product_id]

    # Exclude sneakers with the same normalized base model family
    target_row = df[df["Product ID"] == target_product_id]
    if len(target_row) > 0:
        target_model = target_row.iloc[0]["Model"]
        target_base_model = normalize_base_model(target_model)
        df_candidates = df_candidates[df_candidates["Model"].apply(normalize_base_model) != target_base_model]

    # Exclude any product IDs that are already shown in the Top 5 recommended shoes
    df_candidates = df_candidates[~df_candidates["Product ID"].isin(exclude_ids)]

    # Apply diversity filtering to similar products
    diverse_similar = apply_diversity_filter(df_candidates, top_k)

    return diverse_similar
