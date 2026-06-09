import os
import pandas as pd
from fastapi import FastAPI as fa, HTTPException as ht
from fastapi.middleware.cors import CORSMiddleware as co
from pydantic import BaseModel as bm
from typing import List as li, Optional as op
from dotenv import load_dotenv
import mysql.connector
import uvicorn
# Import the matching engine
from matcher import matching

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "qna_db")

# Create FastAPI app
app = fa(title="Q&A Search Assistant API", version="1.0.0")

# Enable CORS so frontend can talk to backend
app.add_middleware(
    co,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,# Allows cookies to be sent with requests
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

def initialize_db_and_seed():
    try:
        print("Checking/Initializing database and tables...")
        # Connect to MySQL first without database to verify/create database
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.close()
        conn.close()

        # Connect with the specific database name
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Create knowledge_base table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Create source_questions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        # Create question_matches table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            source_question_id INT,
            source_question TEXT NOT NULL,
            matched_question TEXT NOT NULL,
            matched_answer TEXT NOT NULL,
            score FLOAT NOT NULL,
            accuracy_level VARCHAR(20) NOT NULL,
            FOREIGN KEY (source_question_id) REFERENCES source_questions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)

        cursor.close()
        conn.close()
        print("Database schema verification successful.")
    except Exception as e:
        print(f"Error during database initialization: {e}")

# Run database setup verification
initialize_db_and_seed()

# Load Knowledge Base function
def load_knowledge_base():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        df = pd.read_sql("SELECT question, answer FROM knowledge_base", conn)
        conn.close()
        
        if df.empty:
            print("Warning: The 'knowledge_base' table in MySQL is empty.")
            return None
            
        print(f"Loaded knowledge base successfully with {len(df)} rows from MySQL.")
        return df
    except Exception as e:
        print(f"Failed to load knowledge base from MySQL: {e}")
        return None

# Load knowledge base at startup
answers_df = load_knowledge_base()
if answers_df is not None:
    cname2, ans_cname = answers_df.columns[0], answers_df.columns[1]
    print(f"Using database columns: Question='{cname2}', Answer='{ans_cname}'")
else:
    cname2, ans_cname = "question", "answer"

# Pydantic model for query requests
class QueryRequest(bm):
    query: str
    # Optional parameters for matching
    threshold: op[float] = 50.0
    top_k: op[int] = 3
    accuracy_level: op[str] = None # Optional: "strict", "medium", or "loose"

# Pydantic model for match items
class MatchItem(bm):
    matched_question: str
    answer: str
    score: float

# Pydantic model for query responses
class QueryResponse(bm):
    query: str
    matches: li[MatchItem]

# Endpoint for querying the knowledge base
@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    if answers_df is None:# Check if the knowledge base is loaded
        raise ht(status_code=500, detail="Knowledge base not loaded.")
    
    if not req.query.strip():# Check if the query is empty
        return QueryResponse(query=req.query, matches=[])

    # Determine numeric threshold based on accuracy level or fallback to request parameter
    threshold = req.threshold
    if req.accuracy_level:
        lvl = req.accuracy_level.lower().strip()
        if lvl == "strict":
            threshold = 80.0
        elif lvl == "medium":
            threshold = 50.0
        elif lvl == "loose":
            threshold = 30.0

    try:
        # Run matching
        results = matching(
            # Create a single-row DataFrame for the user query
            sheet1=pd.DataFrame({"Question": [req.query]}),
            sheet2=answers_df,
            cname1="Question",
            cname2=cname2,
            ans_cname=ans_cname,
            threshold=threshold,
            top_k=req.top_k
        )
        
        # Create list of match items
        matches = []
        if results and "matches" in results[0]:
            for item in results[0]["matches"]:
                matches.append(MatchItem(
                    matched_question=item["matched_question"],
                    answer=item["answer"],
                    score=item["score"]
                ))
        
        # Return query response
        return QueryResponse(query=req.query, matches=matches)
    except Exception as e:
        raise ht(status_code=500, detail=f"Matching query failed: {str(e)}")

# Endpoint for statistics
@app.get("/api/stats")
async def stats_endpoint():
    # Check if the knowledge base is loaded
    if answers_df is None:
        return {"status": "error", "message": "Knowledge base not loaded."}
    # Return statistics
    return {
        "status": "success",
        "total_records": len(answers_df),
        "columns": list(answers_df.columns)
    }

# Endpoint to reload knowledge base
@app.post("/api/reload")
async def reload_endpoint():
    global answers_df, cname2, ans_cname
    df = load_knowledge_base()
    if df is not None:
        answers_df = df
        cname2, ans_cname = answers_df.columns[0], answers_df.columns[1]
        return {
            "status": "success",
            "message": f"Successfully reloaded knowledge base from MySQL with {len(answers_df)} rows."
        }
    else:
        raise ht(status_code=500, detail="Failed to reload knowledge base from MySQL database.")

# Endpoint to dynamically get suggestions list strictly from MySQL database
@app.get("/api/suggestions")
async def suggestions_endpoint():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT question FROM source_questions")
        questions = [row[0] for row in cursor.fetchall() if row[0]]
        cursor.close()
        conn.close()
        return {"status": "success", "questions": questions}
    except Exception as e:
        raise ht(status_code=500, detail=f"Failed to fetch suggestions from MySQL database: {str(e)}")

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)