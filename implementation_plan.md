# Implementation Plan - Excel Q&A Matching & Approximation System

We are building a complete web application with a **Python FastAPI backend** and a **React + Vite frontend** to perform approximate matching between two Excel sheets (Question Sheet and Answer Sheet) and fetch the relevant answers.

This implementation plan has been updated to reflect the current state of the codebase, including a **code audit and critical bugs identified in the existing backend code**, and to provide a complete, concrete roadmap for the backend endpoints and frontend components.

---

## 🔍 Code Audit & Critical Bugs Identified

During our review of the existing backend files, we identified several runtime and logical errors in `server/matcher.py` and `server/main.py` that must be addressed immediately:

### 1. Critical Runtime Errors in `server/matcher.py`
* **AttributeError in `cleaner` (Line 12)**: 
  ```python
  text=text.lower().trim().strip()
  ```
  *Python strings do not have a `.trim()` method.* This will throw an `AttributeError` on any non-empty string.
  * **Fix**: Change to `text = text.lower().strip()`.
* **NameError in `calculate_tfidf` (Lines 28-31)**:
  ```python
  def calculate_tfidf(queries:list[str],references:list[str])->np.ndarray:
      ...
      if not query or not reference:
          return np.zeros((len(query),len(reference)))
      cleaned_queries = [cleaner(q) for q in query]
      cleaned_references = [cleaner(r) for r in reference]
  ```
  The function arguments are named `queries` and `references`, but the function body references `query` and `reference`, which will throw a `NameError`.
  * **Fix**: Update all body references to use `queries` and `references`.
* **NameError in `matching` (Line 85)**:
  ```python
  "is_conflict": conflict
  ```
  The variable `conflict` is not defined anywhere in the `matching` function, which will cause a `NameError` at runtime.
  * **Fix**: Define a proper conflict detection threshold (e.g., if the top two matches are within 5% score difference, set `conflict = True`).
* **Hardcoded Top-K Retrieval (Line 69)**:
  ```python
  top_matches = row[:1]
  ```
  The `todo.md` and user requirements specify retrieving **Top 3** potential matches to support alternative views and the "Click-to-Swap" feature in the frontend. The current engine only retrieves the single best match and completely ignores any parameter for `top_k`.
  * **Fix**: Add a `top_k` parameter to the matching runner and retrieve `row[:top_k]` matches.

### 2. Syntax Errors & Empty Endpoints in `server/main.py`
* **Syntax Errors**:
  The `server/main.py` file contains incomplete decorators and function declarations without bodies or `pass` statements, and it refers to `@app.post` without first defining the `app` instance:
  ```python
  import pandas as pd 
  from fastapi import FastAPI as fa

  @app.post('/api/upload')
  async def upload_file():
      
  # (No app instance defined, no body, no return statements)
  ```
  * **Fix**: Initialize `app = fa()`, add proper Pydantic schemas, and implement file reading and matching logic using `Pandas` and `openpyxl`.

---

## 🛠️ Proposed Backend Changes

We will fix the errors in `server/matcher.py` and fully implement `server/main.py` to create a robust REST API.

### [MODIFY] [matcher.py](file:///c:/Users/Chirag%20Pradhan/qna/server/matcher.py)
* **Correct all syntax and name errors** (`trim()`, `query` vs `queries`, `reference` vs `references`).
* **Update `matching` function signature**:
  ```python
  def matching(sheet1: pd.DataFrame, sheet2: pd.DataFrame, cname1: str, cname2: str, ans_cname: str, threshold: float, top_k: int = 3) -> list:
  ```
* **Implement robust Conflict Detection**:
  For each question, sort the generated hybrid matches. If `len(row) >= 2`, check the absolute difference between `row[0]["score"]` and `row[1]["score"]`. If `row[0]["score"] >= threshold` and `row[1]["score"] >= threshold` and the difference is `< 5.0` points, set `is_conflict = True` to flag it for the user in the UI.

### [MODIFY] [main.py](file:///c:/Users/Chirag%20Pradhan/qna/server/main.py)
* **Setup API Server**:
  Initialize FastAPI, enable CORS middleware to allow connections from `http://localhost:3000`, and set up a temporary directory to cache uploaded files during the session.
* **`POST /api/upload`**:
  Accepts two uploaded Excel/CSV files (`file1` and `file2`). Parses them using `pandas.read_excel()` or `pandas.read_csv()`, retrieves their columns, extracts the first 5 preview rows, and returns this metadata to the frontend so the user can map the columns.
* **`POST /api/match`**:
  Accepts a JSON payload detailing the column selections, similarity threshold, `top_k`, and temporary file paths. Runs the corrected `matching` engine and returns the matching payload containing all matched rows, Top-K candidates, conflict statuses, and confidence scores.
* **`POST /api/export`**:
  Accepts the current matched results list (including any manual overrides made by the user) and the chosen export mode (`best`, `multi_column`, or `concat`). Generates a downloadable Excel sheet using `pandas` and `openpyxl` with:
  * Highlighted header rows.
  * Formatted columns showing the results.
  * Color-coded confidence scores (e.g., green for high confidence, orange for low confidence, red for conflicts/unmatched).

---

## 🎨 Proposed Frontend Changes (`client`)

We will build the custom React components under `client/src/` with a premium glassmorphic dark-mode palette:

### [MODIFY] [package.json](file:///c:/Users/Chirag%20Pradhan/qna/client/package.json)
Configures standard React dependencies, development proxy to `http://localhost:8000`, and essential utilities like `lucide-react` for beautiful icons.

### [MODIFY] [App.css](file:///c:/Users/Chirag%20Pradhan/qna/client/src/App.css)
Configure modern CSS styling using a curated palette:
* **Slate & Indigo Glassmorphic theme**: Dark-mode base (`#0f172a`), translucent glass panels with `backdrop-filter: blur(12px)` and thin borders (`rgba(255, 255, 255, 0.08)`).
* **Color codes**: High confidence (`#10b981` emerald), Low confidence (`#f59e0b` amber), Conflict/High Alert (`#ef4444` rose), and Indigo theme accents (`#6366f1`).
* **Animations**: Fade-in-up animations for cards and smooth transition states for expander elements.

### [MODIFY] [App.js](file:///c:/Users/Chirag%20Pradhan/qna/client/src/App.js)
Manages the application workflow across three key views:
1. **Upload View**: Prompt user to drag & drop Sheet 1 (Questions) and Sheet 2 (Reference Answers).
2. **Config View**: Show parsed headers, let users select columns, adjust the threshold slider (0-100%), set `top_k`, select the Excel export format, and run the matching engine.
3. **Dashboard/Results View**: Render matching statistics (KPIs) and the central interactable matching spreadsheet table.

### [MODIFY] [FileUpload.js](file:///c:/Users/Chirag%20Pradhan/qna/client/src/FileUpload.js)
* Visual drag-and-drop zone using standard HTML drag events.
* Shows active file stats (name, size, row count preview).
* Validates file extensions (`.xlsx`, `.xls`, `.csv`).

### [MODIFY] [MatchConfig.js](file:///c:/Users/Chirag%20Pradhan/qna/client/src/MatchConfig.js)
* Renders dropdowns for:
  * Sheet 1 Question Column.
  * Sheet 2 Reference Question Column.
  * Sheet 2 Reference Answer Column.
* Threshold slider showing real-time feedback (e.g. *"Only accept matches with >70% confidence"*).
* Top-K selector (retrieving 1 to 5 potential answers).
* Export mode selector:
  * **Best Match Only**: Saves only the single highest-scoring answer.
  * **Multi-Column Export**: Appends multiple solution columns (`Answer 1`, `Answer 2`, etc.).
  * **Merged Concatenation**: Merges multiple answers into one cell with bullet points and scores.

### [MODIFY] [ResultTable.js](file:///c:/Users/Chirag%20Pradhan/qna/client/src/ResultTable.js)
* **Search & Filters**: Search queries, filter by "High Confidence" (>80%), "Low Confidence" (threshold to 80%), and "Conflicts" (is_conflict is true).
* **Interactive Rows**: Displays original rows side-by-side with the primary matched answer and a confidence badge.
* **Expandable Drawer (Click-to-Swap)**:
  * Clicking on a row expands a beautiful glassmorphic sub-panel showing the list of **Top-K matched options**.
  * Each option is rendered as a clean clickable card displaying the reference question, the retrieved answer, and the confidence score.
  * **Manual Override**: Clicking any alternative card instantly swaps it as the active primary match, updating the parent state and final export dataset!

### [MODIFY] [DashboardStats.js](file:///c:/Users/Chirag%20Pradhan/qna/client/src/DashboardStats.js)
* Grid of 4 sleek glassmorphic statistics cards:
  1. **Success Rate**: Percentage of questions matched above threshold.
  2. **Total Processed**: Count of original questions.
  3. **Conflicts Flagged**: Number of rows with overlapping high-confidence matches requiring human audit.
  4. **Low Confidence**: Count of matches scoring near the threshold limit.

---

## 📈 Verification Plan

### 1. Automated Script (Local Testing)
We will run a test script (`test_matcher.py`) in `server/` to verify that `matcher.py` runs without errors, computes correct scores, flags conflicts, and respects the `top_k` limits.

### 2. Manual End-to-End Walkthrough
1. **Launch backend**: Run `uvicorn main:app --reload` on port `8000`.
2. **Launch frontend**: Run `npm start` on port `3000`.
3. **Workflow test**:
   * Upload `questions.xlsx` and `answers.xlsx` from `server/data/`.
   * Map the `Question` column for Sheet 1 and `Question` + `Answer` for Sheet 2.
   * Run the matcher.
   * Expand a row to verify that alternative Top-K solutions display.
   * Perform a Click-to-Swap override and confirm the table updates immediately.
   * Export in "Multi-Column" and "Merged Concatenation" modes and verify the downloaded Excel formatting.
