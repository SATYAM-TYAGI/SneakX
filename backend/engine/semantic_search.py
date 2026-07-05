import numpy as np
from sentence_transformers import SentenceTransformer

# globally cached model instance to avoid loading multiple times
_model_instance = None

def get_sentence_transformer_model():
    """
    Load and return the Sentence Transformer model.
    Lazily loads the model once and caches it.
    """
    global _model_instance
    if _model_instance is None:
        print("Initializing Sentence Transformer model (all-MiniLM-L6-v2)...")
        _model_instance = SentenceTransformer("all-MiniLM-L6-v2")
    return _model_instance

def compute_embedding(text: str, model=None) -> np.ndarray:
    """
    Generate a 384-dimensional embedding vector for a single text string.
    """
    if model is None:
        model = get_sentence_transformer_model()
    
    embedding = model.encode(text)
    return embedding

def build_search_sentence(brand: str = None, shoe_type: str = None, gender: str = None, material: str = None, color: str = None) -> str:
    """
    Generate a simple descriptive search sentence from filters if the query is blank.
    Example: "Nike running shoes for men made from mesh in red color"
    """
    parts = []
    
    # append brand if selected
    if brand:
        parts.append(brand)
        
    # append type or fallback word
    if shoe_type:
        parts.append(shoe_type.lower())
    parts.append("shoes")
    
    # append gender target
    if gender:
        parts.append(f"for {gender.lower()}")

    # append color details
    if color:
        parts.append(f"in {color.lower()} color")
        
    # append material details
    if material:
        parts.append(f"made from {material.lower()}")
        
    # join parts into a natural sentence
    sentence = " ".join(parts)
    print(f"Auto-generated search query from filters: '{sentence}'")
    return sentence
