import re
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer as Tf
from sklearn.metrics.pairwise import cosine_similarity as cs
from operator import itemgetter
def cleaner(text)->str:
    """ Cleaning text by lowercasing, and striping whitespace."""
    if pd.isna(text) or not isinstance(text,str):#check empty cell
        return ""
    text=text.lower().trim().strip()
    return text
def calculate_fuzz(q1:str,q2:str)-> float:
    """Calculate the fuzzy matching score between two strings using RapidFuzz."""
    q1=cleaner(q1)
    q2=cleaner(q2)
    if not q1 or not q2:
        return 0.0
    return float(fuzz.token_set_ratio(q1,q2))#compares the words in the strings based on unique and common words between them using fuzz.ratio
def calculate_tfidf(queries:list[str],references:list[str])->np.ndarray:
    """
    Computes a batch cosine similarity matrix using TF-IDF, utilizing Natural Language 
    Processing (NLP) and information retrieval to convert unstructured text into a format 
    that machine learning algorithms can understand.
    Returns a 2D array of scores in the range [0.0, 100.0].
    """
    if not query or not reference:
        return np.zeros((len(query),len(reference)))
    cleaned_queries = [cleaner(q) for q in query]
    cleaned_references = [cleaner(r) for r in reference]
    vectorizer = Tf(stop_words='english', norm='l2')
    ref_mat = vectorizer.fit_transform(cleaned_references)
    query_mat = vectorizer.transform(cleaned_queries)
    similar_matrix = (cs(query_mat,ref_mat))*100
    return similar_matrix
def matching(sheet1, sheet2, cname1, cname2, ans_cname, threshold):
    """ Pairs rows, returns the Top K matches for each query, and identifies conflicts where multiple strong solutions exist."""
    matched=[]
    s1_questions=sheet1[cname1].tolist()
    s2_questions=sheet2[cname2].tolist()
    # Calculate TF-IDF matrix: shape is (len(s1_questions), len(s2_questions))
    tfidf=calculate_tfidf(s1_questions,s2_questions)
    for i in range(len(s1_questions)):
        q1 = s1_questions[i]
        # we filter using TF-IDF scores first, and only run the slow fuzzy comparison 
        # on the top 10 TF-IDF candidates.
        top_k = np.argsort(tfidf[i])[::-1][:10]
        
        row = []
        for j in top_k:
            fuzzy = calculate_fuzz(q1, s2_questions[j])
            
            # Hybrid combined score (0.6 TF-IDF + 0.4 Fuzzy)
            score = (tfidf[i][j]*0.6) + (fuzzy*0.4)
            
            if score >= threshold:
                val = sheet2.iloc[j][ans_cname]
                anss = "" if pd.isna(val) else str(val)
                row.append({
                    "matched_question": s2_questions[j],
                    "answer": anss,
                    "score": float(score)
                })
        # Sort by score in descending order and get the best match for the prototype
        row.sort(key=itemgetter("score"), reverse=True)
        top_matches = row[:1]  
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

    
