import os
import pandas as pd
from fastapi import FastAPI as fa, HTTPException as ht
from fastapi.middleware.cors import CORSMiddleware as co
from pydantic import BaseModel as bm
from typing import List as li, Optional as op

# Import the matching engine
from matcher import matching

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

# Load Knowledge Base at startup
ANSWERS = os.path.join(os.path.dirname(__file__), "data", "answers.xlsx")
try:
    # Load knowledge base from Excel file
    answers_df = pd.read_excel(ANSWERS)
    # Check if the answers sheet has at least 2 columns
    if len(answers_df.columns) < 2:
        raise ValueError("The answers sheet must contain at least 2 columns (Question and Answer).")
    # Get the column names for the question and answer columns
    cname2, ans_cname = answers_df.columns[0], answers_df.columns[1]
    # Print the number of rows in the knowledge base
    print(f"Loaded knowledge base successfully with {len(answers_df)} rows.")
    # Print the column names for the question and answer columns
    print(f"Using columns: Question='{cname2}', Answer='{ans_cname}'")
# Handle any exceptions that may occur during the loading process
except Exception as e:
    answers_df = None
    print(f"Failed to load knowledge base: {e}")

# Pydantic model for query requests
class QueryRequest(bm):
    query: str
    # Optional parameters for matching
    threshold: op[float] = 50.0
    top_k: op[int] = 3

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

    try:
        # Run matching
        results = matching(
            # Create a single-row DataFrame for the user query
            sheet1=pd.DataFrame({"Question": [req.query]}),
            sheet2=answers_df,
            cname1="Question",
            cname2=cname2,
            ans_cname=ans_cname,
            threshold=req.threshold,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)