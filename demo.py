from difflib import SequenceMatcher
import os
import json
from flask import jsonify, Blueprint, request

matcher_bp = Blueprint('matcher', __name__)

def load_knowledge_base():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(script_dir, 'kb.json')
    
    if not os.path.exists(kb_path):
        print("Error: kb.json not found")
        return []

    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

knowledge_base = load_knowledge_base()

def calculate_fuzzy_score(q1, q2):
    # Convert to lowercase and remove extra spaces for better matching
    q1 = q1.strip().lower()
    q2 = q2.strip().lower()
    
    # Calculate similarity ratio using SequenceMatcher
    similarity_ratio = SequenceMatcher(None, q1, q2).ratio()
    
    # Return the ratio as a percentage
    return similarity_ratio * 100

@matcher_bp.route('/ask', methods=['POST'])
def ask():
    try:
        user_question = request.json.get('question', '').strip()
        
        if not user_question:
            return jsonify({'error': 'No question provided'}), 400
        
        if not knowledge_base:
            return jsonify({'error': 'Knowledge base is empty'}), 500
        
        best_match = None
        highest_score = 0
        
        for item in knowledge_base:
            # Calculate fuzzy score with the current knowledge item
            score = calculate_fuzzy_score(user_question, item['question'])
            
            # Check if this is the best match found so far
            if score > highest_score:
                highest_score = score
                best_match = item
        
        # Threshold to decide if we found a good match
        # Adjust this threshold based on desired accuracy
        threshold = 60 
        
        if highest_score >= threshold and best_match:
            return jsonify({
                'question': best_match['question'],
                'answer': best_match['answer'],
                'score': highest_score
            })
        else:
            return jsonify({
                'question': user_question,
                'answer': 'I am not sure about this. Would you like me to help you with something else?',
                'score': highest_score
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500