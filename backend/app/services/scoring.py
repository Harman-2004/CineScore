from typing import Dict, Optional, Tuple, List, Union

def calculate_normalized_weights(
    imdb_val: Optional[Union[float, str]], 
    tmdb_val: Optional[Union[float, str]], 
    metacritic_val: Optional[Union[float, str]], 
    nlp_val: Optional[Union[float, str]]
) -> Tuple[float, Dict[str, float], List[str], List[str]]:
    """
    Intelligently normalizes rating weights proportionally when some sources are missing.
    
    Default weights:
    IMDb = 40% (0.40)
    TMDb = 20% (0.20)
    Metacritic = 10% (0.10)
    NLP Sentiment = 30% (0.30)
    
    Returns:
    - final_composite_score (float): The dynamic weighted final rating out of 10.
    - effective_weights (Dict[str, float]): Recalculated weights (in decimals) totaling 1.0.
    - available_sources (List[str]): List of active sources.
    - missing_sources (List[str]): List of missing/unresolved sources.
    """
    base_weights = {
        "imdb": 0.40,
        "tmdb": 0.20,
        "metacritic": 0.10,
        "nlp": 0.30
    }
    
    # Helper to safely parse floats, handling N/A, null, etc.
    def safe_float(v) -> Optional[float]:
        if v is None:
            return None
        if isinstance(v, str):
            if v.strip().upper() in ("N/A", "NULL", "NONE", ""):
                return None
            try:
                return float(v)
            except ValueError:
                return None
        try:
            val = float(v)
            return val if val >= 0 else None
        except (ValueError, TypeError):
            return None

    parsed_values = {
        "imdb": safe_float(imdb_val),
        "tmdb": safe_float(tmdb_val),
        "metacritic": safe_float(metacritic_val),
        "nlp": safe_float(nlp_val)
    }
    
    available_sources = []
    missing_sources = []
    
    for src in base_weights:
        if parsed_values[src] is not None:
            available_sources.append(src)
        else:
            missing_sources.append(src)
            
    # Handle absolute fallback where NO sources are available (division by zero safeguard)
    if not available_sources:
        return 0.0, {src: 0.0 for src in base_weights}, available_sources, missing_sources
        
    # Calculate sum of base weights for available sources
    available_weights_sum = sum(base_weights[src] for src in available_sources)
    
    # Proportional weight redistribution
    effective_weights = {}
    for src in base_weights:
        if src in available_sources:
            effective_weights[src] = round(base_weights[src] / available_weights_sum, 4)
        else:
            effective_weights[src] = 0.0
            
    # Calculate weighted composite score
    weighted_sum = sum(parsed_values[src] * effective_weights[src] for src in available_sources)
    
    # In case effective weights round-off slightly deviates from 1.0, normalize sum
    weights_total = sum(effective_weights[src] for src in available_sources)
    final_score = weighted_sum
    if weights_total > 0:
        final_score = weighted_sum / weights_total
        
    return round(final_score, 2), effective_weights, available_sources, missing_sources
