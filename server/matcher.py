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
    return text.lower().strip()

def calculate_fuzz(q1: str, q2: str) -> float:
    """Calculate the fuzzy matching score between two strings using RapidFuzz."""
    q1=cleaner(q1)
    q2=cleaner(q2)
    if not q1 or not q2:
        return 0.0
    return float(fuzz.token_set_ratio(q1,q2))#compares the words in the strings based on unique and common words between them using fuzz.ratio

def calculate_tfidf(query:list[str],reference:list[str])->np.ndarray:
    """
    Computes a batch cosine similarity matrix using TF-IDF, utilizing Natural Language 
    Processing (NLP) and information retrieval to convert unstructured text into a format 
    that machine learning algorithms can understand.
    Returns a 2D array of scores in the range [0.0, 100.0].
    """
    if not query or not reference:
        return np.zeros((len(query),len(reference)))
    vectorizer = Tf(stop_words='english', norm='l2')
    ref_mat = vectorizer.fit_transform([cleaner(r) for r in reference])
    query_mat = vectorizer.transform([cleaner(q) for q in query])
    return cs(query_mat, ref_mat) * 100

def get_topic_words(text: str) -> set[str]:
    """Extract non-generic domain-specific keywords to boost accurate domain matching."""
    generic = {"issue", "issues", "error", "errors", "problem", "problems", "failed",
     "failure", "procedure", "occurred", "facing", "question", "answer", "help", "support",
     "need", "get", "how", "to", "in", "on", "with", "for", "a", "an", "the", "i", "my",
     "me", "we", "our", "you", "your", "am", "is", "are", "was", "were", "be", "been",
     "being", "have", "has", "had", "do", "does", "did", "of", "at", "by", "from", "up",
     "about", "into", "over"}
    return set(re.findall(r'\b\w+\b', cleaner(text))) - generic

def matching(sheet1, sheet2, cname1, cname2, ans_cname, threshold, top_k=3):
    """ Pairs rows, returns the Top K matches for each query, and identifies conflicts where multiple strong solutions exist."""
    matched=[]
    s1_questions=sheet1[cname1].tolist()
    s2_questions=sheet2[cname2].tolist()
    # Calculate TF-IDF matrix: shape is (len(s1_questions), len(s2_questions))
    tfidf=calculate_tfidf(s1_questions,s2_questions)
    for i in range(len(s1_questions)):
        # we filter using TF-IDF scores first on the top 10 TF-IDF candidates.
        top_kc = np.argsort(tfidf[i])[::-1][:10]
        row = []
        q1_topics = get_topic_words(s1_questions[i])
        for j in top_kc:
            s2_topics = get_topic_words(s2_questions[j])
            fuzzy = calculate_fuzz(s1_questions[i], s2_questions[j])
            # Hybrid combined score (0.6 TF-IDF + 0.4 Fuzzy)
            score = (tfidf[i][j]*0.6) + (fuzzy*0.4)
            
            # Boost score if domain keywords match, otherwise penalize if they don't overlap
            if q1_topics & s2_topics:
                score = min(score + 35.0, 100.0)
            else:
                score = max(score - 25.0, 0.0)
            
            if score >= threshold:
                # Retrieve the answer value and handle null/NaN values safely
                val = sheet2.iloc[j][ans_cname]
                anss = "" if pd.isna(val) else str(val)
                # Store the matched question, answer, and similarity score
                row.append({
                    "matched_question": s2_questions[j],
                    "answer": anss,
                    "score": float(score)
                })
                
        # Sort by score in descending order and get the best matches
        row.sort(key=itemgetter("score"), reverse=True)
        # Get the top K matches
        top_matches = row[:top_k]
        # Detect conflicts: two or more matches with high scores
        conflict = len(row) >= 2 and row[0]["score"] >= threshold and row[1]["score"] >= threshold and abs(row[0]["score"] - row[1]["score"]) < 5.0
        # Convert row values safely (handling np.integer types)
        rowi = {}
        for col in sheet1.columns:
            val = sheet1.iloc[i][col]
            if pd.isna(val):
                rowi[col] = None
            elif hasattr(val, 'item'):
                rowi[col] = val.item()
            else:
                rowi[col] = val
        # Append the result for the current row
        matched.append({
            "row_index": i,
            "original_question": s1_questions[i],
            "matches": top_matches,
            "is_conflict": bool(conflict),
            "selected_match_idx": 0,
            "original_row": rowi
        })    
    return matched
