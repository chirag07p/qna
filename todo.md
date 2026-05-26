# Step-by-Step Developer TODO List (Beginner Friendly)

This document is a sequential, step-by-step guide to help you build the Excel Q&A Matching application. Each task includes explanations of **what to do**, **why we are doing it**, and the **exact command to run**.

---

## Folder Structure Map
Before we begin, this is how your workspace folders currently look:
```text
qna/
├── client/
│   ├── react-frontend/   <-- Your React frontend project (already created! ✅)
│   └── vite-frontend/    <-- (Unused Vite project)
├── server/               <-- Your Python FastAPI backend project (already created! ✅)
│   ├── data/             <-- Local sample sheets folder (already created! ✅)
│   ├── matcher.py        <-- Similarity calculations brain (contains bugs to fix! ⚠️)
│   └── main.py           <-- FastAPI web server skeleton (needs full implementation! ⚠️)
├── .venv/                <-- Your Python Virtual Environment sandbox (already created! ✅)
├── requirements.txt      <-- Python dependencies list (already created at root! ✅)
├── todo.md               <-- This checklist (being updated! 🔄)
└── implementation_plan.md <-- Your high-level design plan (updated! ✅)
```

---

## 🚀 PHASE 1: Backend Development & Bug Fixing (Python)

We will fix the critical errors in `matcher.py` first, write the FastAPI endpoints in `main.py`, and test the backend.

---

### Step 0: Pre-requisites & Verification
- [x] **Sample data exists**: Generated `questions.xlsx` and `answers.xlsx` in `server/data/`.
- [x] **Dependencies installed**: `pip install -r requirements.txt` completed.

---

### Step 1: Debug & Complete the Matching Engine (`server/matcher.py`)
- [/] **Audit & Repair Code Quality**:
  - [x] **Fix string cleaner**: Change `text.lower().trim().strip()` to `text.lower().strip()` to prevent string AttributeError.
  - [x] **Fix TF-IDF names**: Change undefined variables `query` and `reference` in `calculate_tfidf()` to `queries` and `references`.
  - [ ] **Implement Top-K Retrieval**: Modify the `matching()` function to accept a `top_k` parameter (default 3) instead of hardcoding `row[:1]`.
  - [ ] **Implement Conflict Detection**: Calculate conflict flags. If the confidence gap between the first and second matched options is less than `5.0` points, set `is_conflict = True` to notify the frontend.
  - [ ] **Verify locally**: Write and run a brief test script `test_matcher.py` inside `server/` to ensure no syntax/runtime crashes exist.

---

### Step 2: Implement FastAPI Router Endpoints (`server/main.py`)
- [ ] **Write Web Server Endpoints**:
  - [ ] **Initialize Server**: Import necessary FastAPI modules, configure CORS for `http://localhost:3000`, and set up temporary file storage.
  - [ ] **Implement `POST /api/upload`**:
    - Handle multi-part file uploads (`file1` and `file2`).
    - Parse using Pandas, extract sheet headers and first 5 rows as previews.
    - Cache files locally in a temporary directory for matching.
  - [ ] **Implement `POST /api/match`**:
    - Receive mapped columns, matching threshold, and `top_k`.
    - Run corrected `matching` engine.
    - Return structured JSON containing all matched records, alternative solutions, and conflict markers.
  - [ ] **Implement `POST /api/export`**:
    - Receive matched data arrays and `exportMode`.
    - Formulate high-quality Excel files (`Best Match`, `Multi-Column`, or `Concatenated`).
    - Style cell borders, headers, and color-code confidence scores using OpenPyXL.
- [ ] **Test Server**: Run `uvicorn main:app --reload` and verify API specs on `http://localhost:8000/docs`.

---

## 🎨 PHASE 2: Frontend Setup & Component Development (React)

Since frontend files are currently empty, we will install libraries, setup the API bridge, and construct the glassmorphic pages.

---

### Step 1: Initialize Libraries & Environment
- [ ] **Install Front-end dependencies**: Run `npm install axios lucide-react` in `client/react-frontend`.
- [ ] **Setup CORS Proxy**: Add `"proxy": "http://localhost:8000"` to `client/react-frontend/package.json` to route API calls correctly.

---

### Step 2: Craft Premium Aesthetics (`client/react-frontend/src/App.css`)
- [ ] **Write Styling Tokens**: Define variables for neon accents, slate backdrops, translucent glass borders, and status colors (emerald, amber, rose).
- [ ] **Style Animations**: Implement fade-ins, hover lifts, pulsing loader circles, and expanding sub-menus.

---

### Step 3: Construct Individual Interface Components
- [ ] **Build `FileUpload.js`**: Create a glowing drag-and-drop zone with dynamic preview tables for both sheets.
- [ ] **Build `MatchConfig.js`**:
  - Create interactive column mapping selectors.
  - Add confidence threshold slider (0-100%) and Top-K counter (1-5).
  - Add export mode selectors with descriptive tooltips.
- [ ] **Build `DashboardStats.js`**: Render glassmorphic KPI cards for success rates, total questions, low confidence counts, and manual conflicts.
- [ ] **Build `ResultTable.js`**:
  - Implement a dense table grid with sorting, searching, and status badge indicators.
  - Create the expandable Drawer. When expanded, render alternative Top-K cards.
  - **Code Click-to-Swap**: Let users click an alternative card to promote it to primary, dynamically updating state.

---

### Step 4: Write Global Controller (`client/react-frontend/src/App.js`)
- [ ] **Manage App State**: Control page navigation (Upload -> Config -> Dashboard), file uploads, selected column keys, matching configs, and matches data.
- [ ] **Integrate API Calls**: Write backend triggers for `/api/upload`, `/api/match`, and `/api/export` (stream as Blob file download).

---

## 🚀 PHASE 3: Deployment & End-to-End Validation
- [ ] Run both servers concurrently.
- [ ] Walk through the complete flow: Upload -> Configure Columns -> View Dashboard & Table -> Swap/Audit a low-confidence match -> Export file.
- [ ] Open the exported spreadsheet to confirm layout and conditional cell colors are applied.
