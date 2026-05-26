import re
import numpy as np
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer as Tf
from sklearn.metrics.pairwise import cosine_similarity as cs
def cleaner(text)->str:
    """ Cleaning text by lowercasing, and striping whitespace."""
    if pd.isna(text) or not isintance(text,str):#check empty cell
        return ""
    text=text.lower().trim().strip()
    return text
def calculate_fuzzy_score(q1:str,q2:str)-> float:
    """Calculate the fuzzy matching score between two strings using TF-IDF and Cosine Similarity."""
    q1=cleaner(q1)
    q2=cleaner(q2)
    if not c1 or not c2:
        return 0.0
    return (fuzz.token_set_ratio(c1,c2))#compares the words in the strings based on unique and common words between them using fuzz.ratio
def calculate_tfidf_scores(ref_question:list[str],query_question:list[str])->np.ndarray:
    """
    Computes a batch cosine similarity matrix using TF-IDF, utilizing Natural Language 
    Processing (NLP) and information retrieval to convert unstructured text into a format 
    that machine learning algorithms can understand.
    Returns a 2D array of scores in the range [0.0, 100.0].
    """
    if not ref_question or not query_question:
        return []
    cleaned_ref = [cleaner(q) for q in ref_question]
    cleaned_query = [cleaner(q) for q in query_question]
    vectorizer = Tf(stop_words='english', norm='l2')
    ref_mat = vectorizer.fit_transform(cleaned_ref)
    query_mat = vectorizer.transform(cleaned_query)
    similar_matrix = (cs(query_mat,ref_mat))*100
    return similar_matrix
def match_sheets(sheet1_df, sheet2_df, col1_name, col2_name, ans_col_name, threshold, top_k=3):
