import re
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer as Tf
from sklearn.metrics.pairwise import cosine_similarity as cs

def cleaner(text) -> str:
    """ Cleaning text by lowercasing, and stripping whitespace."""
    if pd.isna(text) or not isinstance(text, str): # check empty cell
        return ""
    text = text.lower().strip()
    return text

def calculate_fuzz(q1: str, q2: str) -> float:
    """Calculate the fuzzy matching score between two strings using RapidFuzz."""
    q1 = cleaner(q1)
    q2 = cleaner(q2)
    if not q1 or not q2:
        return 0.0
    return float(fuzz.token_set_ratio(q1, q2))

def calculate_tfidf(ref_question: list[str], query_question: list[str]) -> np.ndarray:
    """
    Computes a batch cosine similarity matrix using TF-IDF, utilizing Natural Language 
    Processing (NLP) and information retrieval to convert unstructured text into a format 
    that machine learning algorithms can understand.
    Returns a 2D array of scores in the range [0.0, 100.0] with shape (len(ref_question), len(query_question)).
    """
    if not ref_question or not query_question:
        return np.zeros((len(ref_question), len(query_question)))
    
    cleaned_ref = [cleaner(q) for q in ref_question]
    cleaned_query = [cleaner(q) for q in query_question]
    
    try:
        vectorizer = Tf(stop_words='english', norm='l2')
        ref_mat = vectorizer.fit_transform(cleaned_ref)
        query_mat = vectorizer.transform(cleaned_query)
        similar_matrix = cs(ref_mat, query_mat) * 100
        return np.asarray(similar_matrix)
    except Exception:
        # Fallback to zeros in case vocabulary is empty (e.g. only stop-words or empty strings)
        return np.zeros((len(ref_question), len(query_question)))

def match_sheets(sheet1, sheet2, cname1, cname2, ans_cname, t, top_k=3):
    """ Pairs rows, returns the Top K matches for each query, and identifies conflicts where multiple strong solutions exist."""
    matched = []
    s1_questions = sheet1[cname1].tolist()
    s2_questions = sheet2[cname2].tolist()
    
    tfidf = calculate_tfidf(s1_questions, s2_questions)
    fuzzy = np.zeros((len(s1_questions), len(s2_questions)))
    
    for i in range(len(s1_questions)):
        for j in range(len(s2_questions)):
            fuzzy[i, j] = calculate_fuzz(s1_questions[i], s2_questions[j])
            
    combined = (tfidf * 0.6) + (fuzzy * 0.4)
    
    for i in range(len(s1_questions)):
        row = []
        for j in range(len(s2_questions)):
            score = combined[i, j]
            if score >= t:
                val = sheet2.iloc[j][ans_cname]
                anss = "" if pd.isna(val) else str(val)
                row.append({
                    "matched_question": s2_questions[j],
                    "answer": anss,
                    "score": float(score)
                })
        
        # Sort by score in descending order
        row.sort(key=lambda x: x["score"], reverse=True)
        top_matches = row[:top_k]
        
        # Conflict detection
        conflict = False
        if len(top_matches) >= 2:
            if abs(top_matches[0]["score"] - top_matches[1]["score"]) < 5.0:
                conflict = True
                
        # Prepare original row dictionary (converting NaNs to None for valid JSON serialization)
        rowi = {}
        for col in sheet1.columns:
            val = sheet1.iloc[i][col]
            if pd.isna(val):
                rowi[col] = None
            elif hasattr(val, 'item'):
                rowi[col] = val.item()
            else:
                rowi[col] = val
            
        matched.append({
            "row_index": i,
            "original_question": s1_questions[i],
            "matches": top_matches,
            "is_conflict": conflict,
            "selected_match_idx": 0,
            "original_row": rowi
        })    
    return matched
