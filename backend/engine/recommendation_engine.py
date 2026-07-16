import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def filter_dataset(df, brand=None, shoe_type=None, gender=None, primary_color=None, material=None):
    """
    Hard filter the dataset based on non-empty structured options.
    Always returns a subset of the DataFrame and the corresponding list of row indices.
    """
    filtered_df = df.copy()

    # Apply Brand filter (case-insensitive)
    if brand:
        filtered_df = filtered_df[filtered_df["Brand"].str.lower() == brand.lower()]

    # Apply Type filter (case-insensitive)
    if shoe_type:
        filtered_df = filtered_df[filtered_df["Type"].str.lower() == shoe_type.lower()]

    # Apply Gender filter (case-insensitive)
    if gender:
        filtered_df = filtered_df[filtered_df["Gender"].str.lower() == gender.lower()]

    # Apply Primary Color filter (case-insensitive)
    if primary_color:
        filtered_df = filtered_df[filtered_df["Primary Color"].str.lower() == primary_color.lower()]

    # Apply Material filter if passed via dropdown (case-insensitive substring match)
    if material:
        filtered_df = filtered_df[filtered_df["Material"].str.lower().str.contains(material.lower(), na=False)]

    return filtered_df, filtered_df.index.tolist()

import re

def tokenize_text(text: str) -> list:
    """
    Lowercase text, strip HTML tags, remove punctuation, and return list of tokens.
    """
    if not isinstance(text, str):
        return []
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.findall(r'\b\w+\b', text)

def search_semantic(query_embedding, semantic_query, embeddings_description, bm25_index, df, filtered_indices):
    """
    Calculate similarity score for a query against a filtered subset of shoes.
    
    Why BM25 is used:
    BM25 provides a state-of-the-art lexical ranking algorithm that considers term frequency
    saturation (repeating a word multiple times has diminishing returns) and document length
    normalization (longer descriptions aren't unfairly boosted). This provides strong keyword matching.
    
    How Hybrid Ranking works:
    We combine the semantic understanding of Description embeddings (70% weight) with exact
    keyword matching of BM25 (30% weight). Because BM25 scores are unbounded, we normalize
    them by dividing the scores of our candidates by the maximum BM25 score of the current subset,
    scaling them to [0, 1] so they match the range of cosine similarities.
    """
    if not filtered_indices:
        return pd.DataFrame(columns=df.columns)

    # 1. Cosine similarity on Description embeddings
    desc_subset = embeddings_description[filtered_indices]
    sim_desc = cosine_similarity(query_embedding.reshape(1, -1), desc_subset)[0]

    # 2. BM25 scoring
    tokenized_query = tokenize_text(semantic_query)
    all_bm25_scores = bm25_index.get_scores(tokenized_query)
    subset_bm25_scores = np.array(all_bm25_scores)[filtered_indices]

    # 3. Min-max normalization for BM25 scores in this subset
    max_bm25 = np.max(subset_bm25_scores)
    if max_bm25 > 0:
        normalized_bm25 = subset_bm25_scores / max_bm25
    else:
        normalized_bm25 = np.zeros_like(subset_bm25_scores)

    # 4. Weighted scoring (70% Description, 30% BM25)
    combined_scores = 0.7 * sim_desc + 0.3 * normalized_bm25

    # Add similarity scores to the DataFrame
    df_subset = df.iloc[filtered_indices].copy()
    df_subset["similarity_score"] = combined_scores

    # Sort candidates by combined similarity in descending order
    df_subset = df_subset.sort_values(by="similarity_score", ascending=False)
    return df_subset

def find_similar_products(target_product_id, df, embeddings_identity, embeddings_description, exclude_ids, top_k=20):
    """
    Find the most similar shoes to a target shoe.
    Uses: Brand, Type, Gender, Material, Primary Color, Secondary Color,
    Identity embedding, and Description embedding to determine similarity.
    """
    # Find the target shoe row
    target_rows = df[df["Product ID"] == target_product_id]
    if len(target_rows) == 0:
        return pd.DataFrame(columns=df.columns)
    
    target_idx = target_rows.index[0]
    target_shoe = target_rows.iloc[0]

    # Target embeddings
    target_emb_id = embeddings_identity[target_idx]
    target_emb_desc = embeddings_description[target_idx]

    # Candidate subset: exclude target shoe and any already recommended/selected IDs
    df_candidates = df.copy()
    mask = (df_candidates["Product ID"] != target_product_id) & (~df_candidates["Product ID"].isin(exclude_ids))
    df_candidates = df_candidates[mask]

    if len(df_candidates) == 0:
        return df_candidates

    candidate_indices = df_candidates.index.tolist()

    # Slice candidate embeddings
    emb_id_subset = embeddings_identity[candidate_indices]
    emb_desc_subset = embeddings_description[candidate_indices]

    # Compute cosine similarities
    sim_id = cosine_similarity(target_emb_id.reshape(1, -1), emb_id_subset)[0]
    sim_desc = cosine_similarity(target_emb_desc.reshape(1, -1), emb_desc_subset)[0]

    # Calculate structured trait overlap score (0.1 points per match)
    brand_matches = (df_candidates["Brand"] == target_shoe["Brand"]).astype(float).values
    type_matches = (df_candidates["Type"] == target_shoe["Type"]).astype(float).values
    gender_matches = (df_candidates["Gender"] == target_shoe["Gender"]).astype(float).values
    material_matches = (df_candidates["Material"] == target_shoe["Material"]).astype(float).values
    primary_matches = (df_candidates["Primary Color"] == target_shoe["Primary Color"]).astype(float).values
    secondary_matches = (df_candidates["Secondary Color"] == target_shoe["Secondary Color"]).astype(float).values

    trait_score = 0.1 * (brand_matches + type_matches + gender_matches + material_matches + primary_matches + secondary_matches)

    # Combine embedding similarity and trait matches
    combined_similarity = (sim_id + sim_desc) / 2.0 + trait_score
    df_candidates = df_candidates.copy()
    df_candidates["similarity_score"] = combined_similarity

    # Sort descending and return top_k
    df_candidates = df_candidates.sort_values(by="similarity_score", ascending=False)
    return df_candidates.head(top_k)
