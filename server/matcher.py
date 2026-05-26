import re
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer as Tf
from sklearn.metrics.pairwise import cosine_similarity as cs
def cleaner(text)->str:
    """ Cleaning text by lowercasing, and striping whitespace."""
    if pd.isna(text) or not isintance(text,str):#check empty cell
        return ""
    text=text.lower().trim().strip()
    return text
def calculate_fuzz(q1:str,q2:str)-> float:
    """Calculate the fuzzy matching score between two strings using RapidFuzz."""
    q1=cleaner(q1)
    q2=cleaner(q2)
    if not c1 or not c2:
        return 0.0
    return (fuzz.token_set_ratio(c1,c2))#compares the words in the strings based on unique and common words between them using fuzz.ratio
def calculate_tfidf(ref_question:list[str],query_question:list[str])->np.ndarray:
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
def match_sheets(sheet1, sheet2, cname1, cname2, ans_cname, t, top_k=3):
    """ Pairs rows, returns the Top K matches for each query, and identifies conflicts where multiple strong solutions exist."""
    matched=[]
    s1_questions=sheet1[cname1].tolist()
    s2_questions=sheet2[cname2].tolist()
    tfidf=calculate_tfidf(s1_questions,s2_questions)
    fuzzy=np.zeros((len(s1_questions),len(s2_questions)))
    for i in range(len(s1_questions)):
        for j in range(len(s2_questions)):
            fuzzy[i,j]=calculate_fuzz(s1_questions[i],s2_questions[j])
    combined= (tfidf * 0.6) + (fuzzy * 0.4)
    return combined
    
    
